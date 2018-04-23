# -*- coding: utf-8 -*-
"""
logging
~~~~~~~~~

This module helps with initializing logging using logging config file. The config file utilize 3 handlers
1> Console handler to write debug statements on console
2> Info handler to save info to rotating log file located in logs folder
3> Error handler to save error to rotating log file located in the logs folder
"""

import os
import json
import logging.config
import functools

def log_entry_exit(function):
    """decorator function to log code unit initialization & ending
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(function.__name__)
        logger.info("CODE UNIT STARTED")
        r = function(*args, **kwargs)
        logger.info("CODE UNIT ENDED")
        return r
    return wrapper


def setup_logging(
    default_level=logging.INFO,
    ):
    """Setup logging configuration

    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_path, 'logs/logging_config.json')
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
