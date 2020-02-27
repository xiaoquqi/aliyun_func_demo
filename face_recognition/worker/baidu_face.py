#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from functools import wraps

from aip import AipFace

DEFAULT_IMAGE_TYPE = "URL"
IMAGE_TYPE = "URL"
DEFAULT_GROUP = "AliyunFunctionDemoGroup"
DEFAULT_MATCH_THRESHOLD = 70
DEFAULT_OPTIONS = {
    "max_face_num": 1,
    "face_type": "LIVE",
    "liveness_control": "LOW"
}

# NOTE(Ray): Due to baidu free account limitation to QPS, we need retry
# interface to retry api access.
RETRY_INTERVAL = 5
RETRY_TIMES = 5

def retry(ExceptionToCheck,
          tries=RETRY_TIMES,
          delay=RETRY_INTERVAL,
          backoff=2,
          logger=None):

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (
                        str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        logger.info(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

class QPSLimitation(Exception):
    pass

class BaiduFace(object):

    def __init__(self,
                 app_id,
                 api_key,
                 secret_key,
                 image_type=DEFAULT_IMAGE_TYPE,
                 options=DEFAULT_OPTIONS):
        self.client = AipFace(app_id, api_key, secret_key)
        self.image_type = image_type
        self.options = options

    @retry(QPSLimitation, logger=logging)
    def search_face(self, image_url):
        """Search face in the group"""
        search_options = self.options.copy()
        search_options["match_threshold"] = 70
        search_ret = self.client.search(
            image_url, IMAGE_TYPE, DEFAULT_GROUP, search_options)
        logging.info("Search face returns: %s" % search_ret)
        if search_ret["error_code"] == 18:
            raise QPSLimitation(search_ret["error_msg"])
        return search_ret["result"]

    @retry(QPSLimitation, logger=logging)
    def add_face(self, image_url, username):
        """Add user into face group"""
        add_ret = self.client.addUser(
            image_url, self.image_type, DEFAULT_GROUP, username)
        logging.info("Add face returns: %s" % add_ret)
        if add_ret["error_code"] == 18:
            raise QPSLimitation(add_ret["error_msg"])
        return add_ret["result"]

    @retry(QPSLimitation, logger=logging)
    def detect_face(self, image_url):
        """Detect if the pics contains a person face"""
        detect_ret = self.client.detect(
            image_url, self.image_type, self.options)
        logging.info("Detect face returns: %s" % detect_ret)
        if detect_ret["error_code"] == 18:
            raise QPSLimitation(detect_ret["error_msg"])
        return detect_ret["result"]

    def is_human_face(self, image_url):
        return self.detect_face(image_url)
