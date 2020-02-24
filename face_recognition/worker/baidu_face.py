#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

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

    def search_face(self, image_url):
        """Search face in the group"""
        search_options = self.options.copy()
        search_options["match_threshold"] = 70
        search_ret = self.client.search(
            image_url, IMAGE_TYPE, DEFAULT_GROUP, search_options)
        logging.info("Search face returns: %s" % search_ret)
        return search_ret["result"]

    def add_face(self, image_url, username):
        """Add user into face group"""
        add_ret = self.client.addUser(
            image_url, self.image_type, DEFAULT_GROUP, username)
        logging.info("Add face returns: %s" % add_ret)
        return add_ret["result"]

    def detect_face(self, image_url):
        """Detect if the pics contains a person face"""
        detect_ret = self.client.detect(
            image_url, self.image_type, self.options)
        logging.info("Detect face returns: %s" % detect_ret)
        return detect_ret["result"]

    def is_human_face(self, image_url):
        return self.detect_face(image_url)
