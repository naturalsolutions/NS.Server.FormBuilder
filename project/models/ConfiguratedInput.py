# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
import datetime


# Configurated input
# A configurated input cans have one or more property
class ConfiguratedInput(Base):

    __tablename__ = "ConfiguratedInput"


    pk_ConfiguratedInput      = Column(BigInteger, primary_key=True)

    name          = Column(String(100, 'French_CI_AS'), nullable=False)
    labelFr       = Column(String(300, 'French_CI_AS'), nullable=False)
    labelEn       = Column(String(300, 'French_CI_AS'), nullable=False)
    editMode      = Column(Integer, nullable=False)
    fieldSizeEdit     = Column(String(100, 'French_CI_AS'), nullable=False)
    fieldSizeDisplay     = Column(String(100, 'French_CI_AS'), nullable=False)
    endOfLine     = Column(Boolean, nullable=False)
    startDate     = Column(DateTime, nullable=False)
    curStatus     = Column(Integer, nullable=False)
    type          = Column(String(100, 'French_CI_AS'), nullable=False)
    editorClass   = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClassEdit    = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClassDisplay    = Column(String(100, 'French_CI_AS'), nullable=True)
    
    # linked field section
    linkedFieldTable             = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedFieldIdentifyingColumn = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedField                  = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedFieldset               = Column(String(100, 'French_CI_AS'), nullable=True)

    Properties  = relationship("ConfiguratedInputProperty", cascade="all")

    # constructor
    def __init__(self, name, labelFr, labelEn, editMode, fieldSizeEdit, fieldSizeDisplay, endOfLine, type, editorClass, fieldClassEdit, fieldClassDisplay, linkedFieldTable, linkedFieldIdentifyingColumn, linkedField, linkedFieldset):
        self.name           = name
        self.labelFr        = labelFr
        self.labelEn        = labelEn
        self.editMode       = editMode
        self.fieldSizeEdit      = fieldSizeEdit
        self.fieldSizeDisplay      = fieldSizeDisplay
        self.endOfLine      = endOfLine
        self.type           = type
        self.editorClass    = editorClass
        self.fieldClassEdit     = fieldClassEdit
        self.fieldClassDisplay     = fieldClassDisplay
        self.linkedField    = linkedField
        self.curStatus      = "1"

        # linked field
        self.linkedFieldTable             = linkedFieldTable
        self.linkedFieldIdentifyingColumn = linkedFieldIdentifyingColumn
        self.linkedField                  = linkedField
        self.linkedFieldset               = linkedFieldset

        self.startDate = datetime.datetime.now()

    # Return convert object to JSON object
    def toJSON(self):
        JSONObject = {
            "id"                : self.pk_ConfiguratedInput,
            "labelFr"           : self.labelFr,
            "labelEn"           : self.labelEn,
            "endOfLine"         : self.endOfLine,
            "editMode"          : self.editMode,
            "fieldSizeEdit"         : self.fieldSizeEdit,
            "fieldSizeDisplay"         : self.fieldSizeDisplay,
            "editorClass"       : self.editorClass,
            "fieldClassEdit"        : self.fieldClassEdit,
            "fieldClassDisplay"        : self.fieldClassDisplay,
            "type"              : self.type,
            "name"              : self.name,
            "linkedFieldset"    : self.linkedFieldset,

            # linked field 

            "linkedFieldTable"             : self.linkedFieldTable,
            "linkedFieldIdentifyingColumn" : self.linkedFieldIdentifyingColumn,
            "linkedField"                  : self.linkedField
        }

        for prop in self.Properties:
            JSONObject[prop.name] = prop.getvalue()

        return JSONObject

    # add property to the configurated input
    def addProperty(self, prop):
        self.Properties.append(prop)

    # get Column list except primary key and managed field like curStatus and startDate
    @classmethod
    def getColumnsList(cls):
        return [
            'name',
            'labelFr',
            'labelEn',
            'editMode',
            'fieldSizeEdit',
            'fieldSizeDisplay',
            'endOfLine',
            'type',
            'editorClass',
            'fieldClassEdit',
            'fieldClassDisplay',
            'linkedFieldTable',
            'linkedFieldIdentifyingColumn',
            'linkedField',
            'linkedFieldset'
        ]