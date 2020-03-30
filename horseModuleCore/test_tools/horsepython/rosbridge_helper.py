#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:31:43 2017

@author: juelg@fzi.de
"""


def ros_advertise_cmd(topic, _type, _id=None):
    """
    create a rosbridge advertise command object

    :param topic: the string name of the topic to advertise
    :param _type: ROS msg type as string
    :param _id: optional
    """
    command = {
        "op": "advertise",
        "topic": topic,
        "type": _type
    }

    if _id:
        command["id"] = _id

    return command


def ros_unadvertise_cmd(topic, _id=None):
    """
    create a rosbridge unadvertise command object

    :param topic: the string name of the topic to advertise
    :param _id: optional
    """
    command = {
        "op": "unadvertise",
        "topic": topic
    }

    if _id:
        command["id"] = _id

    return command


def ros_publish_cmd(topic, _msg, _id=None):
    """
    create a rosbridge publish command object

    :param topic: the string name of the topic to publish to
    :param _msg: ROS msg as dict
    :param _id: optional
    """
    command = {
        "op": "publish",
        "topic": topic,
        "msg": _msg
    }

    if _id:
        command["id"] = _id

    return command


def ros_subscribe_cmd(topic, _id=None, _type=None):
    """
    create a rosbridge subscribe command object

    messages on subscribed topics will be sent like this:
    outgoing_msg = {"op": "publish", "topic": topic, "msg": message}
    see rosbridge_library capabilities/subscribe.py

    :param topic: the string name of the topic to subscribe to
    :param _id: optional id to identify subscription for later unsubscribe calls
    :param _type: ROS msg type as string

    not passed on:
    (optional) "throttle_rate": <int>,
    (optional) "queue_length": <int>,
    (optional) "fragment_size": <int>,
    (optional) "compression": <string>
    """
    command = {
        "op": "subscribe",
        "topic": topic
    }

    if _id:
        command["id"] = _id

    if _type:
        command["type"] = _type

    return command


def ros_unsubscribe_cmd(topic, _id=None):
    """
    create a rosbridge unsubscribe command object

    :param topic: the string name of the topic to publish to
    :param _id: optional
    """
    command = {
        "op": "unsubscribe",
        "topic": topic
    }

    if _id:
        command["id"] = _id

    return command


def ros_call_service_cmd(service, _id=None, args=None):
    """
    create a rosbridge call_service command object

    :param service: name of the service to call
    :param _id: optional identifier to link the matching service_response to this request
    :param args: optional dict containing named arguments for the service

    not passed on:
    (optional) "fragment_size": <int>,
    (optional) "compression": <string>
    """
    command = {
        "op": "call_service",
        "service": service
    }

    if _id:
        command["id"] = _id

    if args:
        command["args"] = args

    return command


def ros_advertise_service_cmd(_type, service):
    """
    create a rosbridge advertise_service command object

    :param _type: type of the ROS service
    :param service: name of the service
    """
    command = {
        "op": "advertise_service",
        "type": _type,
        "service": service
    }

    return command


def ros_unadvertise_service_cmd(service):
    """
    create a rosbridge unadvertise_service command object

    :param service: name of the service
    """
    command = {
        "op": "unadvertise_service",
        "service": service
    }

    return command


def ros_service_response_cmd(service, result, _id=None, values=None):
    """
    create a rosbridge service_response command object

    a response to a ROS service call

    :param service: name of the service that was called
    :param result: boolean return value of service callback. True means success, False failure.
    :param _id: if an ID was provided to the call_service request, then the service response will contain the ID
    :param values: dict of the return values. If the service had no return values, then this field
                   can be omitted (and will be by the rosbridge server)
    """
    command = {
        "op": "service_response",
        "service": service,
        "result": result
    }

    if _id:
        command["id"] = _id

    if values:
        command["values"] = values

    return command
