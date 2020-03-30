# -*- coding: utf-8 -*-
""" Example script for Intelligent Imaging course


@author: eendebakpt
"""

#%% Load necessary packages

from __future__ import absolute_import

import sys
import logging
import time
import pickle
import websocket
import platform
import zmq
from collections import deque
import threading

from horseModuleCore.horse_communication import HorseMessageClient
from apscheduler.schedulers.background import BackgroundScheduler

import uuid

from apscheduler.triggers.interval import IntervalTrigger



#%% ZMQ based communication mechanism

if sys.version_info.major == 2:
    WRITE_PORT = 9256
    READ_PORT = 9257
else:
    WRITE_PORT = 9356
    READ_PORT = 9357

try:
    _pickle_protocol = pickle.DEFAULT_PROTOCOL
except:
    # fallback for python2
    _pickle_protocol = 2

_atomic_msg = True


def read_topic(read_function, topic=None, nmax=100):
        """ Read specific topic

        Args: 
            read_function: function to read a single message and return msg, data
            topic (list, str, or None)
            nmax (int)
        Returns:
            topic, data

        """
        n = 0
        while True:
            n = n + 1
            msg, obj = read_function()

            if topic is None:
                # always return object
                return msg, obj
            if len(topic) == 0:
                break

            if isinstance(topic, list):
                if msg in topic:
                    break
            else:
                if topic == msg:
                    break
            if msg is None or n > nmax:
                # to good message found
                msg = ''
                obj = None
                break

        return msg, obj
    
class Publisher():

    def __init__(self, address='tcp://127.0.0.1', port=WRITE_PORT, bind=True, low_latency=False):
        """ Class to publish messages on a ZMQ port """
        context = zmq.Context()
        sock = context.socket(zmq.PUB)
        if low_latency:
            sock.setsockopt(zmq.SNDHWM, 4)
        else:
            sock.setsockopt(zmq.SNDHWM, 10)

        self.bind = bind
        self.addr = address + ':%d' % port
        if bind:
            sock.bind(self.addr)
        else:
            sock.connect(self.addr)

        self.socket = sock

        for ii in range(3):
            self.write_topic('dummy', None)
            time.sleep(0.01)

    def send_message(self, data, topic):
        """ Wrapper function """
        self.write_topic(topic, data)

    def write_topic(self, topic, obj):
        """ Send tag and object and add a timestamp """
        flags = flags = zmq.NOBLOCK
        sock = self.socket

        if _atomic_msg:
            sock.send_pyobj((topic, time.time(), obj),
                            flags=flags, protocol=_pickle_protocol)
        else:
            sock.send_json(topic, flags | zmq.SNDMORE)
            sock.send_json(time.time(), zmq.SNDMORE)

            sock.send_pyobj(obj, flags=flags, protocol=_pickle_protocol)
    def close(self):
        if self.bind:
            self.socket.unbind(self.addr)
        else:
            self.socket.disconnect(self.addr)

    def __del__(self):
        try:
            self.close()
        except Exception as ex:
            logging.info(ex)
            pass


class Receiver:

    def __init__(self, address='tcp://127.0.0.1', port=READ_PORT, bind=False, low_latency=False):
        """ Class to receive messages on a ZMQ port """
        context = zmq.Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt(zmq.SUBSCRIBE, b'')

        if not address.startswith('tcp://'):
            raise Exception('ZMQ address should start with tcp://')
        if low_latency:
            if not platform.system() == 'Windows':
                pass
                # no conflate on receiver, this causes problems
                #sock.setsockopt(zmq.CONFLATE, 1)
            sock.setsockopt(zmq.RCVHWM, 3)
        else:
            sock.setsockopt(zmq.RCVHWM, 200)

        self.bind = bind
        self.addr = address + ':%d' % port
        if bind:
            sock.bind(self.addr)
        else:
            sock.connect(self.addr)
        self.socket = sock
        if low_latency:
            pass
            #sock.setsockopt(zmq.RCVHWM, 4)
            if platform.system() == 'Windows':
                pass
                # no conflate on receiver, this causes problems
                #sock.setsockopt(zmq.CONFLATE, 1)
        else:
            sock.setsockopt(zmq.RCVHWM, 200)

        # self.receive_message = self.receive # not working???

    def flush(self):
        for ii in range(10):
            try:
			
                ss = self.socket.recv(flags=zmq.NOBLOCK)

            except:
                pass

    def receive0(self):
        sock = self.socket
        message = sock.recv()
        return message

    def read_topic(self, topic=None, nmax=100):
        """ Read specific topic 

        Messages with other topics are discarded

        """
        n = 0
        while True:
            n = n + 1
            msg, obj = self.receive(timeout=0)

            if topic is None:
                # always return object
                return msg, obj
            if len(topic) == 0:
                break

            if isinstance(topic, list):
                if msg in topic:
                    break
            else:
                if topic == msg:
                    break
            #print('n %d: msg %s' % (n, msg) )
            if msg is None or n > nmax:
                # to good message found
                msg = ''
                obj = None
                break

        return msg, obj

    def receive_message(self, timeout=None):
        return self.receive(timeout=timeout)

    def receive(self, timeout=None):
        """  Receive a message 

        Arguments:
            timeout (None or int): timeout in miliseconds

        Returns:
            msg (str or None): message name
            obj (Python object)
        """
        sock = self.socket
        timestamp = None
        p = -1
        try:
            if timeout is None:
                p = 0
                if _atomic_msg:
                    (message, timestamp, obj) = sock.recv_pyobj(flags=zmq.NOBLOCK)
                else:
                    message = sock.recv_json(flags=zmq.NOBLOCK)
                    p = 1
                    timestamp = sock.recv_json()
                    obj = sock.recv_pyobj()
                p = 3
            else:
                p = 0
                sock.RCVTIMEO = timeout
                if _atomic_msg:
                    (message, timestamp, obj) = sock.recv_pyobj()
                else:
                    message = sock.recv_json()
                    p = 1
                    timestamp = sock.recv_json()
                    obj = sock.recv_pyobj()
                p = 3
        except zmq.ZMQError as ex:
            if ex.errno == zmq.EAGAIN:
                pass  # no message was ready
                if p > 0:
                    print('## receive: p %d, timeout %s' % (p, timeout))
                    print('   message %s' % message)
                    raise
                else:
                    pass
                    # print('...')
                message = None
                obj = None
            else:
                print('## receive ZMQError: p %s' % p)
                try:
                    print('receive: message %s' % message)
                except:
                    pass
                try:
                    print('receive: timestamp %s' % timestamp)
                except:
                    pass
                raise  # real error
        except Exception as ex:
            print('## receive: p %s' % p)
            try:
                print('receive: message %s' % message)
            except:
                pass
            try:
                print('receive: timestamp %s' % timestamp)
            except:
                pass
            raise  # real error

        return message, obj

    def receive_latest(self, topic):
        mdata = None
        ii = 0
        t = None
        while True:
            tx, mdatax = self.read_topic(topic=topic)
            if mdatax is not None:
                mdata = mdatax
                t = tx
            else:
                break
            ii = ii + 1

        return t, mdata

    def close(self):
                   
            if self.bind:
                  
                self.socket.unbind(self.addr)
                    
            else:
                
                self.socket.disconnect(self.addr)

    def __del__(self):
        try:
            self.close()
                       
        except Exception as ex:
            logging.info(ex)
            print('error when closing connection...')
            pass



def synchronized(method):
    """ Decorator to use class lock instance """

    def new_method(self, *arg, **kws):
        with self.lock:
            return method(self, *arg, **kws)

    return new_method


class message_dispatcher:

    def __init__(self, connections=None, max_messages=100, periodic_pull=0, name='dummy'):
        """  Class to dispatch messages to different clients """
        self.name = name
        
        if connections is None:
            self.connections = [Receiver()]
        else:
            if isinstance(connections, (Receiver, ARMessageClient)):
                self.connections = [connections]
            else:
                self.connections = connections
        self.data = {}
        self.max_messages = max_messages

        self.lock = threading.RLock()
        if periodic_pull:
            self.timer = threading.Timer(
                periodic_pull, self.pull_messages_safe)
            self.timer.start()

        self._debug_iter = 0
        self._last_pull_time = 0

    def add_scheduler(self, dt=4):
        """ Add automatic readout of the messages 
        """
        self._scheduler = BackgroundScheduler()
#        self._scheduler.add_job(self.pull_messages_safe,
#                                trigger='interval', seconds=dt)
        
        trigger = IntervalTrigger(seconds=dt)
        
        self._scheduler.add_job(self.pull_messages_safe,
                                trigger= trigger, seconds=dt)
        self._scheduler.start()

    def show(self):
        print('message_dispatcher:')
        for d in self.data:
            print('  topic %s: %d messages' % (d, len(self.data[d])))

    @synchronized
    def clear_messages(self):
        for k in self.data:
            self.data[k] = deque()

    @synchronized
    def pull_messages_safe(self, *args, **kwargs):
        t0 = time.time()

        try:
            self.pull_messages(*args, **kwargs)
        except websocket._exceptions.WebSocketConnectionClosedException as ex:
            pass
        except Exception as ex:
            print(
                'message_dispatcher: exception in pull_messages_safe. name %s' % self.name)
            raise ex
        dt = time.time() - t0


    @synchronized
    def _clean(self):
        for k in list(self.data):
            if len(self.data[k]) == 0:
                self.data.pop(k)

    def pull_messages(self, nmax=50, nmin=5, dt=0):
        """ Pull messages from the connections
        
        Args:
            nmax (int): max number of messages to get
            nmin (int): min number of tries to get a message
            dt (float): 
        """
        if self._last_pull_time - time.time() > dt:
            return

        self._debug_iter = self._debug_iter + 1
        if self._debug_iter % 100 == 0:
            self._clean()

        try:
            
            for connection in self.connections:
                if connection is None:
                    continue
    
                for ii in range(nmax):

                    if isinstance(connection, (HorseMessageClient)):
    
                        topicx, msg = connection.receive_topic()
                    else:
                        topicx, msg = connection.receive_message()
    
                    if topicx is not None or ii<nmin:
                        try:
                            if not topicx in self.data:

                                self.data[topicx] = deque()
    
                            self.data[topicx].append(msg)
                            if len(self.data[topicx]) > self.max_messages:
                                for ii in range(5):
                                    self.data[topicx].popleft()
                        except Exception as ex:
                            print('topicx %s' % (topicx,))
                            print(ex)
                            raise ex
                    else:

                        break
    
            self._last_pull_time = time.time()
        except Exception as ex:
            print(ex)
            raise ex
            
    def receive_message(self, topic):
        """ Receive a message with specified topic """

        self.pull_messages_safe()
        
        try:
            msg = self.data[topic].popleft()
            return topic, msg
        except:
            return None, None


class ARMessageClient():

    def __init__(self, address=None, port=None, node=None, method='zmq'):
        """ High level message client

        Args:
            adress (str)
            port (None or int)
            method (str): 'zmq' or 'horse'
        """
        self.method = method
        
        if node is None:
            node = 'messageclient-' + str(uuid.uuid4())

        self.address = 'tcp://127.0.0.1'
        
        self.receiver = Receiver(address=self.address)
        self.publisher = Publisher(bind=False, address=self.address)

    def receive_message(self, topic=None):
        """ Recieve a single message

        Args:
            topic (str or None): if not None, only return messages with 
                        specified topic
        Returns:
            topic (str or list): topic of the message
            data (object): any python object containing the data
        """
        if self.method == 'zmq':
            return self.receiver.read_topic(topic)
        elif self.method == 'horse':
            read_function = self.receiver.receive_topic
            return read_topic(read_function, topic=topic)

        else:
            raise Exception('method %s not supported' % self.method)

    def send_message(self, data, topic):
        """ Send a message """
        if self.method == 'zmq':
            self.publisher.write_topic(topic=topic, obj=data)
        elif self.method == 'horse':
            self.publisher.send_message(data=data, topic=topic)
        else:
            raise Exception('method %s not supported' % self.method)

def checkMessageServer(address='tcp://127.0.0.1', sleep_time=0.02, niter=10):
    """ Check the message server is running """
    r = Receiver(address=address)
    p = Publisher(bind=False, address=address)

    if not address.startswith('tcp://127.0.0.1'):
        sleep_time = max(sleep_time, 0.1)
    o = ARobject()
    topic = str(o.objectid)

    for ii in range(5):
        p.write_topic(topic, o)
        time.sleep(sleep_time)
    for ii in range(niter):
        rr = r.read_topic(topic)

        if rr[1] is not None:
            break
        time.sleep(sleep_time)
    if rr[1] is None:
        print('message server not running at %s?' % address)
        return False
    time.sleep(0.02)  # for safety
    return True



