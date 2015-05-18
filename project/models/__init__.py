# -*- coding: utf8 -*-
# 
from sqlalchemy                     import create_engine, Column, Integer, ForeignKey, BigInteger, String, DateTime,Boolean, SmallInteger
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.orm                 import Session, relationship, backref
from sqlalchemy.ext.declarative     import declarative_base

import datetime
import json

# Get class from database
# See database-scripts folder to check database SQL schema
Base = declarative_base()
metadata = Base.metadata

# Form class
# Form has 0 or n Keywords
class Form(Base):
    __tablename__ = 'Form'

    pk_Form          = Column(BigInteger, primary_key=True)

    name                   = Column(String(100, 'French_CI_AS'), nullable=False)
    tag                    = Column(String(300, 'French_CI_AS'), nullable=True)
    labelFr                = Column(String(300, 'French_CI_AS'), nullable=False)
    labelEn                = Column(String(300, 'French_CI_AS'), nullable=False)
    creationDate           = Column(DateTime, nullable=False)
    modificationDate       = Column(DateTime, nullable=True)
    curStatus              = Column(Integer, nullable=False)
    descriptionFr          = Column(String(300, 'French_CI_AS'), nullable=False)
    descriptionEn          = Column(String(300, 'French_CI_AS'), nullable=False)

    # Relationship
    keywords         = relationship("KeyWord_Form")  # A form has many Keywords
    inputs           = relationship("Input")         # A form has many Inputs

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
            "keywordsEn" : keywordsEn
        }

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


# KeyWord Class
# A Keyword can be used by many Form
class KeyWord(Base) :

    __tablename__ = 'KeyWord'

    pk_KeyWord       = Column(BigInteger, primary_key=True)

    name             = Column(String(100, 'French_CI_AS'), nullable=False, unique=True)
    creationDate     = Column(DateTime, nullable=False)
    modificationDate = Column(DateTime, nullable=True)
    curStatus        = Column(Integer, nullable=False)
    lng              = Column(String(2), nullable=False)

    # Constuctor
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


# Unity Class
class Unity(Base) :

    __tablename__ = "Unity"

    pk_Unity      = Column(BigInteger, primary_key=True)
    name          = Column(String(100, 'French_CI_AS'), nullable=False)
    labelFr       = Column(String(300, 'French_CI_AS'))
    labelEn       = Column(String(300, 'French_CI_AS'))

    def toJSON(self):
        return {
            "ID"        : self.pk_Unity,
            "name"      : self.name,
            "labelFr"   : self.labelFr,
            "labelEn"   : self.labelEn
        }


# Input Class
class Input(Base):

    __tablename__ = "Input"

    pk_Input      = Column(BigInteger, primary_key=True)

    fk_form       = Column(ForeignKey('Form.pk_Form'), nullable=False)

    name          = Column(String(100, 'French_CI_AS'), nullable=False)
    labelFr       = Column(String(300, 'French_CI_AS'), nullable=False)
    labelEn       = Column(String(300, 'French_CI_AS'), nullable=False)
    required      = Column(Boolean, nullable=False)
    readonly      = Column(Boolean, nullable=False)
    fieldSize     = Column(String(100, 'French_CI_AS'), nullable=False)
    endOfLine     = Column(Boolean, nullable=False)
    startDate     = Column(DateTime, nullable=False)
    curStatus     = Column(Integer, nullable=False)
    order         = Column(SmallInteger, nullable=True)
    type          = Column(String(100, 'French_CI_AS'), nullable=False)
    editorClass   = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClass    = Column(String(100, 'French_CI_AS'), nullable=True)
    
    # linked field section
    linkedFieldTable             = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedFieldIdentifyingColumn = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedField                  = Column(String(100, 'French_CI_AS'), nullable=True)
    formIdentifyingColumn        = Column(String(100, 'French_CI_AS'), nullable=True)

    Form        = relationship('Form')
    Properties  = relationship("InputProperty")

    # constructor
    def __init__(self, name, labelFr, labelEn, required, readonly, fieldSize, endOfLine, type, editorClass, fieldClass, linkedFieldTable, linkedFieldIdentifyingColumn, linkedField, formIdentifyingColumn, order):
        self.name        = name
        self.labelFr     = labelFr
        self.labelEn     = labelEn
        self.required    = required
        self.readonly    = readonly
        self.fieldSize   = fieldSize
        self.endOfLine   = endOfLine
        self.type        = type
        self.editorClass = editorClass
        self.fieldClass  = fieldClass
        self.linkedField = linkedField
        self.curStatus   = "1"
        self.order       = order

        # linked field
        self.linkedFieldTable             = linkedFieldTable
        self.linkedFieldIdentifyingColumn = linkedFieldIdentifyingColumn
        self.linkedField                  = linkedField
        self.formIdentifyingColumn        = formIdentifyingColumn

        self.startDate = datetime.datetime.now()

    # Update form values
    def update(self, **kwargs):
        self.name        = kwargs['name']
        self.labelFr     = kwargs['labelFr']
        self.labelEn     = kwargs['labelEn']
        self.required    = kwargs['required']
        self.readonly    = kwargs['readonly']
        self.fieldSize   = kwargs['fieldSize']
        self.endOfLine   = kwargs['endOfLine']
        self.editorClass = kwargs['editorClass']
        self.fieldClass  = kwargs['fieldClass']
        self.order       = kwargs['order']

        # linked field
        self.linkedFieldTable             = kwargs['linkedFieldTable']
        self.linkedFieldIdentifyingColumn = kwargs['linkedFieldIdentifyingColumn']
        self.linkedField                  = kwargs['linkedField']
        self.formIdentifyingColumn        = kwargs['formIdentifyingColumn']


    # Return convert object to JSON object
    def toJSON(self):
        JSONObject = {
            "id"          : self.pk_Input,
            "labelFr"     : self.labelFr,
            "labelEn"     : self.labelEn,
            "required"    : self.required,
            "endOfLine"   : self.endOfLine,
            "readonly"    : self.readonly,
            "fieldSize"   : self.fieldSize,
            "editorClass" : self.editorClass,
            "fieldClass"  : self.fieldClass,
            "type"        : self.type,
            "order"        : self.order,

            # linked field 

            "linkedFieldTable"             : self.linkedFieldTable,
            "linkedFieldIdentifyingColumn" : self.linkedFieldIdentifyingColumn,
            "linkedField"                  : self.linkedField,
            "formIdentifyingColumn"        : self.formIdentifyingColumn
        }
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
            'required',
            'readonly',
            'fieldSize',
            'endOfLine',
            'type',
            'editorClass',
            'fieldClass',
            'linkedFieldTable',
            'linkedFieldIdentifyingColumn',
            'linkedField',
            'formIdentifyingColumn',
            'order'
        ]


# Input Property
class InputProperty(Base):

    __tablename__ = "InputProperty"

    pk_InputProperty = Column(BigInteger, primary_key=True)

    fk_Input         = Column(ForeignKey('Input.pk_Input'), nullable=False)

    name             = Column(String(255, 'French_CI_AS'), nullable=False)
    value            = Column(String(255, 'French_CI_AS'), nullable=False)
    creationDate     = Column(DateTime, nullable=False)
    valueType        = Column(String(10, 'French_CI_AS'), nullable=False)

    Input = relationship('Input')

     # constructor
    def __init__(self, name, value, valueType):
        self.name         = name
        self.value        = value
        self.valueType    = valueType
        self.creationDate = datetime.datetime.now()

    # Return value casted on the correct format
    def getvalue(self):
        if self.valueType == "Boolean":
            return bool(self.value)
        elif self.valueType == "Number":
            return int(self.value)
        elif self.valueType == "Double":
            return float(int(self.value))
        else:
            return self.value


# Configurated input
# A configurated input cans have one or more property
class ConfiguratedInput(Base):

    __tablename__ = 'ConfiguratedInput'

    pk_ConfiguratedInput = Column(BigInteger, primary_key=True)

    name                 = Column(String(100, 'French_CI_AS'), nullable=False)
    labelFr              = Column(String(300, 'French_CI_AS'), nullable=False)
    labelEn              = Column(String(300, 'French_CI_AS'), nullable=False)
    required             = Column(Boolean, nullable=False)
    readonly             = Column(Boolean, nullable=False)
    fieldSize            = Column(String(100, 'French_CI_AS'), nullable=False)
    endOfLine            = Column(Boolean, nullable=False)
    startDate            = Column(DateTime, nullable=False)
    curStatus            = Column(Integer, nullable=False)
    order                = Column(SmallInteger, nullable=True)

    type                 = Column(String(100, 'French_CI_AS'), nullable=False)
    editorClass          = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClass           = Column(String(100, 'French_CI_AS'), nullable=True)

    Properties           = relationship("ConfiguratedInputProperty")

    # constructor
    def __init__(self, name, labelFr, labelEn, required, readonly, fieldSize, endOfLine, type, editorClass, fieldClass, order):
        self.name        = name
        self.labelFr     = labelFr
        self.labelEn     = labelEn
        self.required    = required
        self.readonly    = readonly
        self.fieldSize   = fieldSize
        self.endOfLine   = endOfLine
        self.type        = type
        self.order       = order
        self.editorClass = editorClass
        self.fieldClass  = fieldClass
        self.curStatus   = "1"

        self.startDate = datetime.datetime.now()

    # Return convert object to JSON object
    def toJSON(self):
        JSONObject = {
            "labelFr"     : self.labelFr,
            "labelEn"     : self.labelEn,
            "required"    : self.required,
            "endOfLine"   : self.endOfLine,
            "readonly"    : self.readonly,
            "fieldSize"   : self.fieldSize,
            "editorClass" : self.editorClass,
            "fieldClass"  : self.fieldClass,
            "type"        : self.type,
            "order"        : self.order
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
            'required',
            'readonly',
            'fieldSize',
            'endOfLine',
            'type',
            'order',
            'editorClass',
            'fieldClass',
        ]


# Configurated input property
class ConfiguratedInputProperty(Base):
    __tablename__ = 'ConfiguratedInputProperty'

    pk_ConfiguratedInputProperty = Column(BigInteger, primary_key=True)

    fk_ConfiguratedInput         = Column(ForeignKey('ConfiguratedInput.pk_ConfiguratedInput'), nullable=False)

    name                         = Column(String(255, ''), nullable=False)
    value                        = Column(String(255, 'French_CI_AS'), nullable=False)
    creationDate                 = Column(DateTime, nullable=False)
    valueType                    = Column(String(10, 'French_CI_AS'), nullable=False)

    ConfiguratedInput = relationship('ConfiguratedInput')

    # constructor
    def __init__(self, name, value, valueType):
        self.name         = name
        self.value        = value
        self.valueType    = valueType
        self.creationDate = datetime.datetime.now()

    # Return value casted on the correct format
    def getvalue(self):
        if self.valueType == "Boolean":
            return bool(self.value)
        elif self.valueType == "Number":
            return int(self.value)
        elif self.valueType == "Double":
            return float(int(self.value))
        else:
            return self.value


# Database connexion
# We use pyodbc and SQL Server for the moment
with open("project/config/config.json", "r") as config:
        data = json.loads( config.read() )

sqlConnexion = data["sql"]["url"] if 'sql' in data and 'url' in data['sql'] else 'mssql+pyodbc://CORLEONE-PC/formbuilder'

engine = create_engine(sqlConnexion)

Base.metadata.create_all(engine)

session = Session(engine)