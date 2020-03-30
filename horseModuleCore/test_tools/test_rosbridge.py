#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:31:43 2017

@author: juelg@fzi.de
"""

import time

from pythonbridge import HorseBridge
from rosbridge_helper import *

# see https://github.com/websocket-client/websocket-client
from websocket import create_connection, WebSocketTimeoutException
import json


# %% Python client for Horse messagebus
class WebsocketRosbridge(object):
    def __init__(self, address='ws://localhost:9091/', timeout=.1):
        """
        Args:
            address (str): default connection is to localhost
            timeout (float): timeout to use for receiving messages
        """
        self.ws = create_connection(address)
        self.ws.settimeout(timeout)
        self.verbose = 2

    def send_message(self, data, topic='dummy_TOPIC', response_message_id='', receivers="*", priority=2):
        """ Send message to server

        Args:
            :param data: data (dict) to be sent
            :param topic: not used
            :param response_message_id:
            :param receivers:
            :param priority:
        """
        msg = json.dumps(data)

        if self.verbose >= 2:
            print(msg)
        self.ws.send(msg)

    def receive_message(self):
        try:
            result = self.ws.recv()
        except WebSocketTimeoutException:
            result = None
        return result

    def __repr__(self):
        return '<%s: at 0x%x>' % (self.__class__.__name__, id(self))


class TestRosbridge:
    def __init__(self, backend="horse_messagebus_rosbridge", port=8082):
        if backend == "horse_messagebus_rosbridge":
            address = 'ws://localhost:{}/horse/message'.format(port)
            self.messagebus_topic_to_rosbridge = 'rosbridge'
            self.messagebus_receiver = 'rosbridge'

            self.hp = HorseBridge(address, node='test_rosbridge')
            print(self.hp)

            self.hp.init_node()
            r = self.hp.receive_message()  # TODO: check/filter for ROS/rosbridge related messages
            print(r)
            # TODO: check for correct response ID instead;
            # other received messages could be newly published subscription data

        else:
            address = 'ws://localhost:{}/'.format(port)
            self.messagebus_topic_to_rosbridge = 'rosbridge'
            self.messagebus_receiver = 'rosbridge'

            self.hp = WebsocketRosbridge(address=address)
            print(self.hp)

    def test_advertise_publish_unadvertise(self, ros_topic, message_type, iterations=10):
        """
        advertise a topic, publish $iterations messages on it and then unadvertise the topic

        :param ros_topic: e.g. /horse_data
        :param message_type: ros msgs type, eg std_msgs/String
        :param iterations: (int)
        """

        print("Advertising ros_topic {}...".format(ros_topic))
        self.hp.send_message(ros_advertise_cmd(ros_topic, message_type),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(.2)

        print(self.hp.receive_message())  # processing statement
        print(self.hp.receive_message())  # echo of message sent

        print("iterating {} times".format(iterations))

        # %% Loop
        for ii in range(iterations):
            time.sleep(1)
            msg = "Iteration %d'..." % ii
            print(msg)
            ros_msg = {"data": msg}  # std_msgs/String = {string data = ...}
            self.hp.send_message(ros_publish_cmd(ros_topic, ros_msg),
                                 topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
            time.sleep(.2)

            print(self.hp.receive_message())  # "Message processed through message bus:<echo>"
            # print(self.hp.receive_message())  # "<echo>" # no "echo" if receivers is restricted to rosbridge

        print("Unadvertising ros_topic {}...".format(ros_topic))
        self.hp.send_message(ros_unadvertise_cmd(ros_topic),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(1)

        print(self.hp.receive_message())  # "Message processed through message bus:<echo>"
        print(self.hp.receive_message())  # "<echo>"

    def test_subscribe_read_unsubscribe(self, ros_topic, message_type, iterations=10):
        """
        subscribe to a topic, look for publish messages on it and then unsubscribe the topic

        :param ros_topic: e.g. /horse_data
        :param message_type: ros msgs type, eg std_msgs/String
        :param iterations: (int)
        """

        print("Subscribing ros_topic {}...".format(ros_topic))
        self.hp.send_message(ros_subscribe_cmd(topic=ros_topic, _type=message_type,
                                               _id="test_subscribe_read_unsubscribe"),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(.2)

        print(self.hp.receive_message())  # processing statement
        print(self.hp.receive_message())  # echo of message sent

        print("iterating {} times".format(iterations))

        # %% Loop
        for ii in range(iterations):
            time.sleep(1)
            msg = "Iteration %d..." % ii
            print(msg)

            print(self.hp.receive_message())  # "Message processed through message bus:<echo>"
            print(self.hp.receive_message())  # "<echo>"

        print("Unsubscribing ros_topic {}...".format(ros_topic))
        self.hp.send_message(ros_unsubscribe_cmd(ros_topic),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(2)

        print(self.hp.receive_message())  # "Message processed through message bus:<echo>"
        print(self.hp.receive_message())  # "<echo>"

    def test_call_service(self, service_name, service_type, service_args):
        """
        call a service, wait for the response

        :param service_name: e.g. "/rosapi/get_param_names"
        :param service_type: e.g. "rosapi/GetParamNames"
        :param service_args: dict, e.g. {"name":"a_name"}
        """

        print("Call service  {} of type {} with args {}...".format(service_name, service_type, service_args))
        self.hp.send_message(ros_call_service_cmd(service=service_name, args=service_args),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(.2)

        print(self.hp.receive_message())  # processing statement

        reply = self.hp.receive_message()
        # obj = json.loads(reply)  # TODO: optimize, decode only first layer to get Topic,...
        # obj = {k.lower(): v for k, v in obj.items()}  # make all keys lowercase
        # # TODO: get "payload", print
        print(reply)

        print(self.hp.receive_message())

    def test_offer_service(self, service_name, service_type, service_args):
        """
        advertise service, call service, deliver response, unadvertise service

        :param service_name: e.g. "/rosapi/get_param_names"
        :param service_type: e.g. "rosapi/GetParamNames"
        :param service_args: dict, used to call the offered service
        """

        print("Offer service  {} of type {}...".format(service_name, service_type))
        self.hp.send_message(ros_advertise_service_cmd(service=service_name, _type=service_type),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(.2)
        print(self.hp.receive_message())  # processing statement

        print("Call service  {} of type {} with args {}...".format(service_name, service_type, service_args))
        self.hp.send_message(ros_call_service_cmd(service=service_name, args=service_args),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(.2)
        print(self.hp.receive_message())  # processing statement

        # TODO: get call_service from rosbridge, extract "id"
        print(self.hp.receive_message())
        print(self.hp.receive_message())

        # # TODO remove
        # print("TODO REMOVE: not sending service response to check rosbridge bug: "
        #       "rosbridge will start fully consuming one core while no response on externally advertised service")

        # send service_response to rosbridge
        print("Send service_response  {} of type {} with args {}...".format(service_name, service_type, service_args))
        self.hp.send_message(ros_service_response_cmd(service=service_name, result=True,
                                                      values={"success": True, "message": "SetBool success"},
                                                      _id="service_request:/horse/test_service:1"),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(.2)
        print(self.hp.receive_message())  # processing statement

        # TODO: currently rosbridge_messagebus has high CPU usage from receiving a messagebus-hosted call_service
        #       request up to reception of a matching service_response. investigate RosbridgeProtocol internals

        # TODO: receive and check service_response
        print(self.hp.receive_message())
        print(self.hp.receive_message())

        print("Unadvertise service  {}...".format(service_name))
        self.hp.send_message(ros_unadvertise_service_cmd(service=service_name),
                             topic=self.messagebus_topic_to_rosbridge, receivers=self.messagebus_receiver)
        time.sleep(.2)
        print(self.hp.receive_message())  # processing statement
        print(self.hp.receive_message())
        print(self.hp.receive_message())

    def main(self):
        # prepare ros data
        pub_topic = "/horse_data"
        pub_type = "std_msgs/String"

        sub_topic1 = "/rosout"
        sub_type1 = "rosgraph_msgs/Log"

        sub_topic2 = "/horse_text"
        sub_type2 = "std_msgs/String"

        service_name1 = "/rosapi/get_param_names"
        service_type1 = "rosapi/GetParamNames"
        service_args1 = {}

        service_name2 = "/rosapi/get_param"
        service_type2 = "rosapi/GetParam"
        service_args2 = {'name': '/rosbridge_messagebus/port', 'default': "0"}  # string name, string default

        service_name3 = "/rosapi/get_param"
        service_type3 = "rosapi/GetParam"
        service_args3 = {"name": "rosdistro", "default": "foo"}  # string name, string default

        service_args4 = {'name': '/absolutely_nonexistent', 'default': "42"}  # string name, string default

        self.test_advertise_publish_unadvertise(pub_topic, pub_type, iterations=5)

        self.test_subscribe_read_unsubscribe(sub_topic1, sub_type1, iterations=3)
        # self.test_subscribe_read_unsubscribe(sub_topic2, sub_type2, iterations=3)

        self.test_call_service(service_name1, service_type1, service_args1)  # expected output: list of ROS parameters
        self.test_call_service(service_name2, service_type2, service_args2)  # expected output: 8082
        self.test_call_service(service_name3, service_type3, service_args3)  # expected output: indigo / kinetic
        self.test_call_service(service_name3, service_type3, service_args4)  # expected output: 42

        # similar to CLI command "rosservice list"
        self.test_call_service("/rosapi/services", "rosapi/Services", {})

        # similar to CLI command "rosservice info <service>"
        self.test_call_service("/rosapi/service_type", "rosapi/ServiceType", {'service': '/rosapi_services'})

        # advertise service, call service, deliver response, unadvertise service
        self.test_offer_service("/horse/test_service", "std_srvs/SetBool", {'data': True})

        print("Done")


if __name__ == '__main__':
    # test_messagebus = False
    test_messagebus = True

    if test_messagebus:
        # connect to MessageBus
        test_horse_bridge = TestRosbridge()
        test_horse_bridge.main()

    else:
        # Run the same tests against the standard rosbridge_websocket to differentiate
        # between bugs in rosbridge_messagebus and in rosbridge_library and rosapi.
        test_rosbridge = TestRosbridge(backend="websocket_rosbridge", port=9091)
        test_rosbridge.main()

