#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from app import db
 
class TimestampMixin(object):
    created_at = db.Column(db.DateTime,
                           default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime,
                           onupdate=lambda: datetime.utcnow()) 


class Person(db.Model, TimestampMixin):
    __tablename__ = "persons"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(40), index=True)
    tag = db.Column(db.String(255))
    faces = db.relationship("Face")

    @property
    def serialize(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "tag": self.tag,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "faces": [f.serialize for f in self.faces]
        }


class Face(db.Model, TimestampMixin):
    __tablename__ = "faces"
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer,
                          db.ForeignKey("persons.id"),
                          index=True)
    url = db.Column(db.String(255))
    person = db.relationship("Person",
        backref=db.backref("persons",
                         uselist=True,
                         cascade="delete,all"))

    @property
    def serialize(self):
        return {
            "id": self.id,
            "url": self.url
        }
