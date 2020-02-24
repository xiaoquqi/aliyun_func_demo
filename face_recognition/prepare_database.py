#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Env requirements:
#
# pip install pymysql
#
# export DB_USER=func_compute
# export DB_PASSWORD=xxxxxx
# export DB_HOST=rm-2ze42t12m819480ewqo.mysql.rds.aliyuncs.com

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from worker.db.models import Base

# Get database connection from env
env_dict = os.environ
db_user = env_dict["DB_USER"]
db_password = env_dict["DB_PASSWORD"]
db_host = env_dict["DB_HOST"]

connection = "mysql+pymysql://%s:%s@%s/face_recognition?charset=utf8" % (db_user, db_password, db_host)
engine = create_engine(connection, echo=True)

session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
