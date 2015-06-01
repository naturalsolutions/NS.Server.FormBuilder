# -*- coding: utf8 -*-

import datetime
from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base


# Relation between Form and KeyWord
class KeyWord_Form(Base):

    __tablename__ = "KeyWord_Form"

    pk_KeyWord_Form = Column(BigInteger, primary_key=True)

    fk_KeyWord      = Column(ForeignKey('KeyWord.pk_KeyWord'), nullable=False)
    fk_Form         = Column(ForeignKey('Form.pk_Form'), nullable=False)

    creationDate    = Column(DateTime, nullable=False)
    curStatus       = Column(Integer, nullable=False)

    Form    = relationship('Form')
    KeyWord = relationship('KeyWord')

    #   Constructor
    def __init__(self):
        self.creationDate = datetime.datetime.now()
        self.ModifDate = datetime.datetime.now()
        self.curStatus = "1"

    # JSON serialization
    def toJSON(self):
        return self.KeyWord.toJSON()