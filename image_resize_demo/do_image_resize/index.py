# -*- coding: utf-8 -*-

import logging
import json
import logging
import os
import oss2

from PIL import Image

RESIZE_SIZES = [16, 32, 64]

logging.basicConfig(
        format="%(asctime)s %(process)s %(levelname)s [-] %(message)s",
        level=logging.INFO
)

def handler(event, context):
    evt_list = json.loads(event)
    creds = context.credentials

    # NOTE(Ray): If the service ran in local, use Auth method.
    local = bool(os.getenv("local", ""))
    if local:
        logging.info("Running function in local...")
        auth = oss2.Auth(creds.access_key_id,
                         creds.access_key_secret)
    else:
        auth = oss2.StsAuth(creds.access_key_id,
                            creds.access_key_secret,
                            creds.security_token)

    # Parse the event to get the source object info.
    evt = evt_list["events"][0]
    source_bucket_name = evt["oss"]["bucket"]["name"]

    if local:
        endpoint = "oss-" + evt["region"] + ".aliyuncs.com"
    else:
        endpoint = "oss-" + evt["region"] + "-internal.aliyuncs.com"

    source_bucket = oss2.Bucket(auth, endpoint, source_bucket_name)
    object_name = evt["oss"]["object"]["key"]

    target_bucket_name = "ray-s3-testing-resize"
    target_bucket = oss2.Bucket(auth, endpoint, target_bucket_name)

    save_object_path = os.path.join("/tmp", object_name)
    logging.info("Downloading file %s to %s..." % (
        object_name, save_object_path))
    source_bucket.get_object_to_file(object_name, save_object_path)

    basename, extname = os.path.splitext(save_object_path)
    for size in RESIZE_SIZES:
        resize_object_name = "%s_%sx%s.%s" % (
            object_name, size, size, extname)
        resize_image_path = "%s_%sx%s.%s" % (
            basename, size, size, extname)
        logging.info("Converting file to %s..." % resize_image_path)
        resize(save_object_path, resize_image_path, size, size)
        logging.info("Uploading file %s to OSS %s..." % (
            resize_image_path, resize_object_name))
        target_bucket.put_object_from_file(
            resize_object_name, resize_image_path)

def resize(image_path, resize_image_path, weight, height):
    img = Image.open(image_path)
    img = img.resize((weight, height), Image.ANTIALIAS)
    img.save(resize_image_path)
