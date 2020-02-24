# -*- coding: utf-8 -*-
import logging
import json
import os
import oss2
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from baidu_face import BaiduFace
from db.models import Base, Person, Face

# Baidu
APP_ID = "18547158"
API_KEY = "XdVvubLK5Pn1wjGdGEmrU7zn"
SECRET_KEY = "mj7FoorzEaaIxCMiofCG9oGCSPwQjHtQ"

IMAGE_TYPE = "URL"
DEFAULT_GROUP = "AliyunFunctionDemoGroup"
DEFAULT_MATCH_THRESHOLD = 70
DEFAULT_OPTIONS = {
    "max_face_num": 1,
    "face_type": "LIVE",
    "liveness_control": "LOW"
}

# Database
DB_USER = "func_compute"
DB_PASSWORD = "P@ssw0rd"
DB_NAME = "face_recognition"
DB_CHARSET = "charset=utf8"
DB_EXTERNAL_HOST = "rm-2ze42t12m819480ewqo.mysql.rds.aliyuncs.com"
DB_INTERNAL_HOST = "rm-2ze42t12m819480ew125010.mysql.rds.aliyuncs.com"

# Get current run model
LOCAL = bool(os.getenv("local", ""))

db_session = None

def initializer(context):
    logging.basicConfig(
            format="%(asctime)s %(process)s %(levelname)s [-] %(message)s",
            level=logging.INFO
    )
    db_host = DB_EXTERNAL_HOST if LOCAL else DB_INTERNAL_HOST
    db_conn = "mysql+pymysql://%s:%s@%s/%s?%s" % (
        DB_USER, DB_PASSWORD, db_host, DB_NAME, DB_CHARSET)
    logging.info("Try to connect database using %s..." % db_conn)
    db_engine = create_engine(db_conn, echo=True)

    # https://www.alibabacloud.com/help/zh/doc-detail/94670.htm#python
    global db_session
    db_session = sessionmaker(bind=db_engine)

def handler(event, context):
    evt_list = json.loads(event)
    creds = context.credentials

    # NOTE(Ray): If the service ran in local, use Auth method.
    if LOCAL:
        logging.info("Running function in local...")
        auth = oss2.Auth(creds.access_key_id,
                         creds.access_key_secret)
    else:
        auth = oss2.StsAuth(creds.access_key_id,
                            creds.access_key_secret,
                            creds.security_token)

    evt = evt_list["events"][0]
    source_bucket_name = evt["oss"]["bucket"]["name"]

    endpoint = "oss-" + evt["region"] + ".aliyuncs.com"

    source_bucket = oss2.Bucket(auth, endpoint, source_bucket_name)
    object_name = evt["oss"]["object"]["key"]

    bucket_url = "http://" + source_bucket_name + "." + endpoint
    object_url = bucket_url + "/" + object_name
    logging.info("Object url is %s" % object_url)

    baidu_face = BaiduFace(APP_ID, API_KEY, SECRET_KEY)

    if not baidu_face.is_human_face(object_url):
        logging.warn("Ignore object %s due to "
                     "no person face found." % object_url)
        return

    face = baidu_face.search_face(object_url)
    logging.info("Search face returns: %s" % face)
    if not face:
        logging.info("Found new human, creating new person...")
        add_new_human_face(object_url, baidu_face)
    else:
        score = face["user_list"][0]["score"]
        if score == 100:
            logging.warn("Ignore %s due to same pic is "
                         "uploaded again." % object_url)
        else:
            person_uuid = face["user_list"][0]["user_id"]
            logging.info("Found new face, update database...")
            update_new_human_face(person_uuid, object_url, baidu_face)

def add_new_human_face(url, baidu_face):
    person_uuid = str(uuid.uuid4()).replace("-", "")
    new_person = Person(uuid=person_uuid)
    face = Face(url=url, person=new_person)
    s = db_session()
    s.add(new_person)
    s.add(face)
    s.commit()
    baidu_face.add_face(url, person_uuid)

def update_new_human_face(uuid, url, baidu_face):
    s = db_session()
    find_person = s.query(Person).filter_by(uuid=uuid).first()
    face = Face(url=url, person=find_person)
    s.add(face)
    s.commit()
    baidu_face.add_face(url, uuid)
