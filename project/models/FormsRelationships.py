# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class FormsRelationships(Base):
    __tablename__   = 'FormsRelationships'

    parent_Form     = Column(String(100, 'French_CI_AS'), ForeignKey('Form.name'), nullable=False, primary_key= True)
    child_Form      = Column(String(100, 'French_CI_AS'), ForeignKey('FormsRelationships.parent_Form'))

    childs          = relationship('FormsRelationships')
    Forms           = relationship('Form')

    # Constructor
    def __init__(self, parentFormName, childFormName):
        print('FormRelationships Inited with parent ', parentFormName, ' and ', childFormName)
        self.parent_Form      = parentFormName
        self.child_Form       = childFormName

    def update(self, parentFormName, childFormName):

        self.parent_Form      = parentFormName
        self.child_Form       = childFormName

    def to_json(self):

        return {
            "parentFormName"     : self.parent_Form,
            "childFormName"      : self.child_Form
        }

    def toJSON(self):
        json = self.to_json()
        
        return json

    @classmethod
    def getColumnList(cls):
        return [
            'parentFormName' ,
            'childFormName'
        ]
