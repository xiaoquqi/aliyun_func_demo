#!/usr/bin/env python
# coding=utf-8

import logging
import os

from flask import make_response
from flask import jsonify
from sqlalchemy.orm import joinedload


try:
  from urllib.parse import urlparse
except:
  from urlparse import urlparse

from app import app, db
from models import Person, Face

# Database
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_CHARSET = "charset=utf8"
DB_EXTERNAL_HOST = os.getenv("DB_EXTERNAL_HOST", "")
DB_INTERNAL_HOST = os.getenv("DB_INTERNAL_HOST", "")

# Get current run model
LOCAL = bool(os.getenv("local", ""))

db_host = DB_EXTERNAL_HOST if LOCAL else DB_INTERNAL_HOST
db_conn = "mysql+pymysql://%s:%s@%s/%s?%s" % (
    DB_USER, DB_PASSWORD, db_host, DB_NAME, DB_CHARSET)
app.config['SQLALCHEMY_DATABASE_URI'] = db_conn

base_path = ""

def initializer(environ):
    logging.basicConfig(
        format="%(asctime)s %(process)s %(levelname)s [-] %(message)s",
        level=logging.INFO
    )

@app.route("/persons", methods=["GET"])
def get_persons():
    result = [p.serialize for p in Person.query.options(
        joinedload("faces")).all()]
    return jsonify(result)

def handler(environ, start_response):
    parsed_tuple = urlparse(environ["fc.request_uri"])
    li = parsed_tuple.path.split("/")
    global base_path
    if not base_path:
        base_path = "/".join(li[0:5])
    return app(environ, start_response)
