from sqlalchemy                 import Column, Date, Integer, String, Table, ForeignKey
from project.models          import Base, Session
from sqlalchemy.orm             import relationship, backref
from sqlalchemy                 import create_engine, UniqueConstraint

import os
import sys
from datetime import date, datetime

# ---------------------------------------------------------------------
# Association class
class Association(Base):

    __tablename__   = 'associationProtocolKeyword'

    protocol_id     = Column(Integer, ForeignKey('Protocols.id'),   primary_key = True )
    keyword_id      = Column(Integer, ForeignKey('Keywords.id'),    primary_key = True )
    keyword         = relationship("Keyword")

    def serialize(self):
        return self.keyword.serialize()

# ---------------------------------------------------------------------
# Protocol table / class declaration
class Protocol(Base):

    __tablename__   = "Protocols"

    # Class attributes definitions
    id              = Column (Integer, primary_key = True)
    name            = Column (String(255), unique = True, nullable = False)
    path            = Column (String(255), unique = True, nullable = False)
    description     = Column (String, nullable = False)

    keywords        = relationship("Association", backref="protocol")
    versions        = relationship ("Version")

    # constraints
    UniqueConstraint('name', name='uix_1')

    # constructor
    def __init__ (self, name, description, path):
        self.name           = name
        self.description    = description
        self.path           = path

    # Add keyword
    def addKeyword(self, newKeyword):
        a = Association()
        a.keyword = newKeyword
        self.keywords.append(a)

    # Add version
    def addVersion(self, version):
        self.versions.append(version)

    # serialization
    def serialize (self):
        # serialize protocol versions
        str = []
        for each in self.versions: str.append (each.serialize())
        # serialize protocol keywords
        keys = []
        for each in self.keywords : keys.append (each.serialize())

        return {
            "id"            : self.id,
            "name"          : self.name,
            "description"   : self.description,
            "keywords"      : keys,
            "version"       : str
        }

# ---------------------------------------------------------------------
# Keyword class
class Keyword (Base) :

    __tablename__   = "Keywords"

    id      = Column (Integer, primary_key = True)
    text    = Column (String(255), unique = True, nullable = False)

    def __init__ (self, text) :
        self.text = text

    def serialize (self):
        return {
            "id" : self.id,
            "text" : self.text
        }

# ---------------------------------------------------------------------
# Unity class
class Unity(Base):

    __tablename__ = "Unities"

    id      = Column (Integer, primary_key = True)
    text    = Column (String(255), unique = True, nullable = False)

    def __init__ (self):
        self.text = text

    def serialize (self):
        return {
            "id" : self.id,
            "text" : self.text
        }

# ---------------------------------------------------------------------
# Version table / class declaration
# One protocol has one or many versions
class Version(Base):

    __tablename__ = "Versions"

    id          = Column (Integer, primary_key = True)
    comment     = Column (String, nullable = False)
    createdAt   = Column (Date)
    protocol_id = Column (Integer, ForeignKey('Protocols.id'))

    def __init__ (self, comment, current):
        self.createdAt  = current
        self.comment    = comment

    def serialize (self):
        return {
            "id"        : self.id,
            "comment"   : str (self.comment),
            "createdAt" : self.createdAt.strftime("%Y-%m-%d_%H-%M-%S")
        }