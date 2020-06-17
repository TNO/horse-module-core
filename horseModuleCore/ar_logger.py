# -*- coding: utf-8 -*-
"""
Created on Tue May 22 14:07:42 2018

@author: HORSE
"""

import logging

import logging.handlers

import os
    
def ARLogger(log_filename = 'log.txt'):
    
    # if not os.path.exists('logs'):
        
    #     os.makedirs('logs')
    
    fmt = '%(asctime)s %(levelname)s %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    
    ar_logger = logging.getLogger('ARLogger')
    ar_logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
              log_filename, maxBytes=10000*4, backupCount=5)

    formatter = logging.Formatter(fmt, datefmt)

    handler.setFormatter(formatter)

    ar_logger.addHandler(handler)
    
    return ar_logger