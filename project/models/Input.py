# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
from ..models.InputTrad import InputTrad

import datetime


# Input Class
class Input(Base):

    __tablename__ = "Input"

    pk_Input      = Column(BigInteger, primary_key=True)

    fk_form       = Column(ForeignKey('Form.pk_Form'), nullable=False)

    name          = Column(String(100, 'French_CI_AS'), nullable=False)
    # labelFr       = Column(String(300, 'French_CI_AS'), nullable=False)
    # labelEn       = Column(String(300, 'French_CI_AS'), nullable=False)
    editMode      = Column(Integer, nullable=False)
    fieldSize     = Column(String(100, 'French_CI_AS'), nullable=False)
    atBeginingOfLine = Column(Boolean, nullable=False)
    startDate     = Column(DateTime, nullable=False)
    curStatus     = Column(Integer, nullable=False)
    order         = Column(SmallInteger, nullable=True)
    type          = Column(String(100, 'French_CI_AS'), nullable=False)
    editorClass   = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClassEdit    = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClassDisplay    = Column(String(100, 'French_CI_AS'), nullable=True)
    originalID              = Column(BigInteger, nullable=True)
    
    # linked field section
    linkedFieldTable             = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedField                  = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedFieldset               = Column(String(100, 'French_CI_AS'), nullable=True)

    Form        = relationship('Form')
    Properties  = relationship("InputProperty", cascade="all")
    InputTrad   = relationship("InputTrad", cascade="all")

    # constructor
    def __init__(self, name, labelFr, labelEn, editMode, fieldSize, atBeginingOfLine, type, editorClass, fieldClassEdit, fieldClassDisplay, linkedFieldTable, linkedField, linkedFieldset, order):
        print ("new name is " + name)
        self.name           = name
        # self.labelFr        = labelFr
        # self.labelEn        = labelEn
        self.editMode       = editMode
        self.fieldSize      = fieldSize
        self.atBeginingOfLine = atBeginingOfLine
        self.type           = type
        self.editorClass    = editorClass
        self.fieldClassEdit     = fieldClassEdit
        self.fieldClassDisplay     = fieldClassDisplay
        self.linkedField    = linkedField
        self.curStatus      = "1"
        self.order          = order

        # linked field
        self.linkedFieldTable             = linkedFieldTable
        self.linkedField                  = linkedField
        self.linkedFieldset               = linkedFieldset

        self.startDate = datetime.datetime.now()

    # Update form values
    def update(self, **kwargs):
        self.name        = kwargs['name']
        # self.labelFr     = kwargs['labelFr']
        # self.labelEn     = kwargs['labelEn']
        self.editMode    = kwargs['editMode']
        self.fieldSize   = kwargs['fieldSize']
        self.atBeginingOfLine   = kwargs['atBeginingOfLine']
        self.editorClass = kwargs['editorClass']
        self.fieldClassEdit  = kwargs['fieldClassEdit']
        self.fieldClassDisplay  = kwargs['fieldClassDisplay']
        self.order       = kwargs['order']

        # linked field
        self.linkedFieldTable             = kwargs['linkedFieldTable']
        self.linkedField                  = kwargs['linkedField']
        self.linkedFieldset               = kwargs['linkedFieldset']

    # Return convert object to JSON object
    def toJSON(self):
        JSONObject = {
            "id"                : self.pk_Input,
            # "labelFr"           : self.labelFr,
            # "labelEn"           : self.labelEn,
            "atBeginingOfLine"  : self.atBeginingOfLine,
            "editMode"          : self.editMode,
            "fieldSize"         : self.fieldSize,
            "editorClass"       : self.editorClass,
            "fieldClassEdit"    : self.fieldClassEdit,
            "fieldClassDisplay" : self.fieldClassDisplay,
            "originalID"        : self.originalID,
            "type"              : self.type,
            "order"             : self.order,
            "name"              : self.name,
            "linkedFieldset"    : self.linkedFieldset,

            # linked field 

            "linkedFieldTable"             : self.linkedFieldTable,
            "linkedField"                  : self.linkedField,

            "translations"  : self.getTranslations()
        }

        for prop in self.Properties :
            JSONObject[prop.name] = prop.getvalue()

        #TODO Find out why this exists ?
        #if (self.type == 'ChildForm') :
        #    JSONObject[realChildFormName] = 

        return JSONObject

    # add property to the configurated input
    def addProperty(self, prop):
        self.Properties.append(prop)

    def getProperty(self, propname):
        for InputProp in self.Properties:
            if InputProp.name == propname:
                return InputProp.value
        return ""

    # get Column list except primary key and managed field like curStatus and startDate
    @classmethod
    def getColumnsList(cls):
        return [
            'name',
            # 'labelFr',
            # 'labelEn',
            'editMode',
            'fieldSize',
            'atBeginingOfLine',
            'type',
            'editorClass',
            'fieldClassEdit',
            'fieldClassDisplay',
            'linkedFieldTable',
            'linkedField',
            'linkedFieldset',
            'order'
        ]

    def getTranslations(self):
        translations = dict()
        allTrad = self.InputTrad
        for each in allTrad:
            translations[each.fk_Language] = each.toJSON()
        return translations