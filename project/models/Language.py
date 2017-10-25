# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base


class Language(Base):

    __tablename__ = 'Language'

    pk_Name = Column(String(2, 'French_CI_AS'), primary_key=True)

    Label = Column(String(100, 'French_CI_AS'), nullable=False)
    Description = Column(String(300, 'French_CI_AS'), nullable=False)

    def __init__(self, label, description):
        self.Label = label
        self.Description = description

    def update(self, label, description):
        self.Label = label
        self.Description = description

    def toJSON(self):
        return {
            "Name"  : self.pk_Name,
            "Label"    : self.Label,
            "Description"    : self.Description
        }

    @classmethod
    def getColumnsList(cls):
        return [
            "Name",
            "Label",
            "Description",
        ]