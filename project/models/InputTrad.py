# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base


class InputTrad(Base):

    __tablename__ = 'InputTrad'

    pk_inputtrad = Column(BigInteger, primary_key=True)
    fk_Input = Column(ForeignKey('Input.pk_Input'), nullable=False)
    fk_Language = Column(ForeignKey('Language.pk_Name'), nullable=False)

    Name = Column(String(255, 'French_CI_AS'), nullable=False)

    Input = relationship('Input')

    def __init__(self, name):
        self.Name = name

    def update(self, name):
        self.Name = name

    def toJSON(self):
        return {
            "Language": self.fk_Language,
            "Name": self.Name
        }

    @classmethod
    def getColumnsList(cls):
        return [
            "Language",
            "Name"
        ]
