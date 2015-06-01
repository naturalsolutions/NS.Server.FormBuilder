# -*- coding: utf8 -*-

from sqlalchemy import *
from .base import Base
import datetime


# KeyWord Class
# A Keyword can be used by many Form
class KeyWord(Base):

    __tablename__ = 'KeyWord'

    pk_KeyWord       = Column(BigInteger, primary_key=True)

    name             = Column(String(100, 'French_CI_AS'), nullable=False)
    creationDate     = Column(DateTime, nullable=False)
    modificationDate = Column(DateTime, nullable=True)
    curStatus        = Column(Integer, nullable=False)
    lng              = Column(String(2), nullable=False)

    # Constructor
    def __init__(self, name, lng):
        self.name             = name
        self.creationDate     = datetime.datetime.now()
        self.modificationDate = datetime.datetime.now()
        self.curStatus        = "1"
        self.lng              = lng

    # Serialize a KeyWord object in JSON format
    def toJSON(self):
        return {
            "id"            : self.pk_KeyWord,
            "name"          : self.name,
            "creationDate"  : self.creationDate.strftime("%Y-%m-%d"),
            "ModifDate"     : self.modificationDate.strftime("%Y-%m-%d"),
            "curStatus"     : self.curStatus,
            "lng"           : self.lng
        }