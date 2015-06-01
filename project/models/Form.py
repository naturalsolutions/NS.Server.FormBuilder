# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
from .KeyWord_Form import  KeyWord_Form
from .KeyWord import KeyWord
import datetime


class Form(Base):
    __tablename__ = 'Form'

    pk_Form          = Column(BigInteger, primary_key=True)

    name                   = Column(String(100, 'French_CI_AS'), nullable=False, unique=True)
    tag                    = Column(String(300, 'French_CI_AS'), nullable=True)
    labelFr                = Column(String(300, 'French_CI_AS'), nullable=False)
    labelEn                = Column(String(300, 'French_CI_AS'), nullable=False)
    creationDate           = Column(DateTime, nullable=False)
    modificationDate       = Column(DateTime, nullable=True)
    curStatus              = Column(Integer, nullable=False)
    descriptionFr          = Column(String(300, 'French_CI_AS'), nullable=False)
    descriptionEn          = Column(String(300, 'French_CI_AS'), nullable=False)

    # Relationship
    keywords         = relationship("KeyWord_Form", cascade="delete")
    fieldsets        = relationship("Fieldset", cascade="all")
    inputs           = relationship("Input", cascade="all")

    # Constructor
    def __init__(self, **kwargs):
        self.name                   = kwargs['name']
        self.tag                    = kwargs['tag']
        self.labelFr                = kwargs['labelFr']
        self.labelEn                = kwargs['labelEn']
        self.descriptionEn          = kwargs['descriptionEn']
        self.descriptionFr          = kwargs['descriptionFr']
        self.creationDate           = datetime.datetime.now()
        self.modificationDate       = datetime.datetime.now()
        self.curStatus              = "1"

    # Update form values
    def update(self, **kwargs):
        self.name                   = kwargs['name']
        self.tag                    = kwargs['tag']
        self.labelFr                = kwargs['labelFr']
        self.labelEn                = kwargs['labelEn']
        self.descriptionEn          = kwargs['descriptionEn']
        self.descriptionFr          = kwargs['descriptionFr']
        self.modificationDate       = datetime.datetime.now()

    def getFieldset(self):
        fieldsets = []
        for each in self.fieldsets:
            fieldsets.append(each.toJSON())
        return fieldsets

    # Serialize a form in JSON object
    def toJSON(self):
        keywordsFr = []
        keywordsEn = []
        tmpKeyword = None
        for each in self.keywords :
            tmpKeyword = each.toJSON()
            if tmpKeyword['lng'] == 'FR':
                del tmpKeyword['lng']
                keywordsFr.append (tmpKeyword)
            else:
                del tmpKeyword['lng']
                keywordsEn.append (tmpKeyword)
        return {
            "id"                       : self.pk_Form,
            "name"                     : self.name,
            "tag"                      : self.tag,
            "labelFr"                  : self.labelFr,
            "labelEn"                  : self.labelEn,
            "creationDate"             : "" if self.creationDate == 'NULL' or self.creationDate is None else self.creationDate.strftime("%Y-%m-%d"),
            "modificationDate"         : "" if self.modificationDate == 'NULL' or self.modificationDate is None else self.modificationDate.strftime("%Y-%m-%d"),
            "curStatus"                : self.curStatus,
            "descriptionFr"            : self.descriptionFr,
            "descriptionEn"            : self.descriptionEn,
            "keywordsFr" : keywordsFr,
            "keywordsEn" : keywordsEn,
            "fieldsets" : self.getFieldset()
        }

    def recuriseToJSON(self):
        json = self.toJSON()
        inputs = {}
        for each in self.inputs:
            inputs[each.name] = each.toJSON()

        json['schema'] = inputs

        return json

    # Add keyword to the form
    def addKeywords(self, KeyWordList, Language):
        for each in KeyWordList:
            a = KeyWord_Form()
            a.KeyWord = KeyWord(each, Language)
            #a.Form = self
            self.keywords.append(a)

    # Add Input to the form
    def addInput(self, newInput):
        self.inputs.append(newInput)

    # Add fieldset to the form
    def addFieldset(self, fieldset):
        self.fieldsets.append(fieldset)

    # return a list of all form's inputs id
    def getInputsIdList(self):
        inputsIdList = []
        for i in self.inputs:
            inputsIdList.append(i.pk_Input)
        return inputsIdList

    @classmethod
    def getColumnList(cls):
        return [
            'name'         ,
            'tag'          ,
            'descriptionFr',
            'descriptionEn',
            'keywordsFr'   ,
            'keywordsEn'   ,
            'labelFr'      ,
            'labelEn'      ,
            'schema'       ,
            'fieldsets'
        ]
