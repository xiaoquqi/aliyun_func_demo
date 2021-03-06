#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TimestampMixin(object):
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, onupdate=lambda: datetime.utcnow())


class Person(Base, TimestampMixin):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(40), index=True)
    tag = Column(String(255))


class Face(Base, TimestampMixin):
    __tablename__ = "faces"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"), index=True)
    url = Column(String(255))
    person = relationship(
        Person,
        backref=backref("persons",
                         uselist=True,
                         cascade="delete,all"))
