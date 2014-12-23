from sqlalchemy                     import create_engine, Column, Integer, ForeignKey, BigInteger, String, DateTime
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.orm                 import Session, relationship, backref
from sqlalchemy.ext.declarative     import declarative_base

import datetime

# Get class from database
# See database-scripts folder to check database SQL schema
Base = declarative_base()
metadata = Base.metadata

# Form class
# Form has 0 or n Keywords
class Form(Base):
    __tablename__ = 'Form'

    pk_Form          = Column(BigInteger, primary_key=True)

    Name                   = Column(String(100, 'French_CI_AS'), nullable=False)
    LabelFR                = Column(String(300, 'French_CI_AS'), nullable=False)
    LabelEN                = Column(String(300, 'French_CI_AS'), nullable=False)
    CreationDate           = Column(DateTime, nullable=False)
    ModificationDate       = Column(DateTime, nullable=True)
    CurStatus              = Column(Integer, nullable=False)
    DescriptionFR          = Column(String(collation='French_CI_AS'), nullable=False)
    DescriptionEN          = Column(String(collation='French_CI_AS'), nullable=False)

    # Relationship
    keywords         = relationship("KeyWord_Form")  # A form has many Keywords
    inputs           = relationship("Input")         # A form has many Inputs

    # Constructor
    def __init__(self, **kwargs):
        self.Name                   = kwargs['Name']
        self.LabelFR                = kwargs['LabelFR']
        self.LabelEN                = kwargs['LabelEN']
        self.DescriptionEN          = kwargs['DescriptionEN']
        self.DescriptionFR          = kwargs['DescriptionFR']
        self.CreationDate           = datetime.datetime.now()
        self.ModificationDate       = datetime.datetime.now()
        self.CurStatus              = "1"

    # Update form values
    def update(self, **kwargs):
        self.Name                   = kwargs['Name']
        self.LabelFR                = kwargs['LabelFR']
        self.LabelEN                = kwargs['LabelEN']
        self.DescriptionEN          = kwargs['DescriptionEN']
        self.DescriptionFR          = kwargs['DescriptionFR']
        self.ModificationDate       = datetime.datetime.now()

    # Serialize a form in JSON object
    def toJSON(self):
        inputs = {}
        for each in self.inputs:
            inputs[each.Name] = each.toJSON()
        keywordsFR = []
        keywordsEN = []
        tmpKeyword = None
        for each in self.keywords :
            tmpKeyword = each.toJSON()
            if tmpKeyword['Lng'] == 'FR':
                del tmpKeyword['Lng']
                keywordsFR.append (tmpKeyword)
            else:
                del tmpKeyword['Lng']
                keywordsEN.append (tmpKeyword)
        return {
            "ID"                       : self.pk_Form,
            "Name"                     : self.Name,
            "LabelFR"                  : self.LabelFR,
            "LabelEN"                  : self.LabelEN,
            "CreationDate"             : self.CreationDate.strftime("%Y-%m-%d"),
            "ModificationDate"         : self.ModificationDate.strftime("%Y-%m-%d"),
            "CurStatus"                : self.CurStatus,
            "DescriptionFR"            : self.DescriptionFR,
            "DescriptionEN"            : self.DescriptionEN,
            "KeywordsFR"               : keywordsFR,
            "KeywordsEN"               : keywordsEN,
            "Schema"                   : inputs
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
            'Name'         ,
            'DescriptionFR',
            'DescriptionEN',
            'KeywordsFR'   ,
            'KeywordsEN'   ,
            'LabelFR'      ,
            'LabelEN'      ,
            'Schema'       ,
            'Fieldsets'
        ]


# KeyWord Class
# A Keyword can be used by many Form
class KeyWord(Base) :

    __tablename__ = 'KeyWord'

    pk_KeyWord       = Column(BigInteger, primary_key=True)

    Name             = Column(String(100, 'French_CI_AS'), nullable=False, unique=True)
    CreationDate     = Column(DateTime, nullable=False)
    ModificationDate = Column(DateTime, nullable=True)
    CurStatus        = Column(Integer, nullable=False)
    Lng              = Column(Integer, nullable=False)

    # Constuctor
    def __init__(self, name, Lng):
        self.Name             = name
        self.CreationDate     = datetime.datetime.now()
        self.ModificationDate = datetime.datetime.now()
        self.CurStatus        = "1"
        self.Lng              = Lng

    # Serialize a KeyWord object in JSON format
    def toJSON(self):
        return {
            "ID"            : self.pk_KeyWord,
            "Name"          : self.Name,
            "CreationDate"  : self.CreationDate.strftime("%Y-%m-%d"),
            "ModifDate"     : self.ModificationDate.strftime("%Y-%m-%d"),
            "CurStatus"     : self.CurStatus,
            "Lng"           : self.Lng
        }


# Relation between Form and KeyWord
class KeyWord_Form(Base):

    __tablename__ = "KeyWord_Form"

    pk_KeyWord_Form = Column(BigInteger, primary_key=True)

    fk_KeyWord      = Column(ForeignKey('KeyWord.pk_KeyWord'), nullable=False)
    fk_Form         = Column(ForeignKey('Form.pk_Form'), nullable=False)

    CreationDate    = Column(DateTime, nullable=False)
    CurStatus       = Column(Integer, nullable=False)

    Form    = relationship('Form')
    KeyWord = relationship('KeyWord')

    #   Constructor
    def __init__(self):
        self.CreationDate = datetime.datetime.now()
        self.ModifDate = datetime.datetime.now()
        self.CurStatus = "1"

    # JSON serialization
    def toJSON(self):
        return self.KeyWord.toJSON()


# Unity Class
class Unity(Base) :

    __tablename__ = "Unity"

    pk_Unity      = Column(BigInteger, primary_key=True)
    Name          = Column(String(100, 'French_CI_AS'), nullable=False)
    LabelFR       = Column(String(300, 'French_CI_AS'))
    LabelEN       = Column(String(300, 'French_CI_AS'))

    def toJSON(self):
        return {
            "ID"        : self.pk_Unity,
            "Name"      : self.Name,
            "LabelFR"   : self.LabelFR,
            "LabelEN"   : self.LabelEN
        }


# Input Class
class Input(Base):

    __tablename__ = "Input"

    pk_Input      = Column(BigInteger, primary_key=True)

    fk_form       = Column(ForeignKey('Form.pk_Form'), nullable=False)

    Name          = Column(String(100, 'French_CI_AS'), nullable=False)
    LabelFR       = Column(String(300, 'French_CI_AS'), nullable=False)
    LabelEN       = Column(String(300, 'French_CI_AS'), nullable=False)
    IsRequired    = Column(BIT, nullable=False)
    IsReadOnly    = Column(BIT, nullable=False)
    FieldSize     = Column(String(100, 'French_CI_AS'), nullable=False)
    IsEOL         = Column(BIT, nullable=False)
    StartDate     = Column(DateTime, nullable=False)
    CurStatus     = Column(Integer, nullable=False)
    InputType     = Column(String(100, 'French_CI_AS'), nullable=False)
    EditorClass   = Column(String(100, 'French_CI_AS'), nullable=True)
    FieldClass    = Column(String(100, 'French_CI_AS'), nullable=True)

    Form        = relationship('Form')
    Properties  = relationship("InputProperty")

    # constructor
    def __init__(self, Name, LabelFR, LabelEN, IsRequired, IsReadOnly, FieldSize, IsEOL, InputType, EditorClass, FieldClass):
        self.Name        = Name
        self.LabelFR     = LabelFR
        self.LabelEN     = LabelEN
        self.IsRequired  = IsRequired
        self.IsReadOnly  = IsReadOnly
        self.FieldSize   = FieldSize
        self.IsEOL       = IsEOL
        self.InputType   = InputType
        self.EditorClass = EditorClass
        self.FieldClass  = FieldClass
        self.CurStatus  = "1"

        self.StartDate = datetime.datetime.now()

    # Update form values
    def update(self, **kwargs):
        self.Name        = kwargs['Name']
        self.LabelFR     = kwargs['LabelFR']
        self.LabelEN     = kwargs['LabelEN']
        self.IsRequired  = kwargs['IsRequired']
        self.IsReadOnly  = kwargs['IsReadOnly']
        self.FieldSize   = kwargs['FieldSize']
        self.IsEOL       = kwargs['IsEOL']
        self.EditorClass = kwargs['EditorClass']
        self.FieldClass  = kwargs['FieldClass']


    # Return convert object to JSON object
    def toJSON(self):
        JSONObject = {
            "ID"          : self.pk_Input,
            "LabelFR"     : self.LabelFR.decode('latin-1').encode("utf-8"),
            "LabelEN"     : self.LabelEN,
            "IsRequired"  : self.IsRequired,
            "IsEOL"       : self.IsEOL,
            "IsReadOnly"  : self.IsReadOnly,
            "FieldSize"   : self.FieldSize,
            "EditorClass" : self.EditorClass,
            "FieldClass"  : self.FieldClass,
            "InputType"   : self.InputType
        }

        for prop in self.Properties:
            JSONObject[prop.Name] = prop.getValue()

        return JSONObject

    # add property to the configurated input
    def addProperty(self, prop):
        self.Properties.append(prop)

    # get Column list except primary key and managed field like curStatus and StartDate
    @classmethod
    def getColumnsList(cls):
        return [
            'Name',
            'LabelFR',
            'LabelEN',
            'IsRequired',
            'IsReadOnly',
            'FieldSize',
            'IsEOL',
            'InputType',
            'EditorClass',
            'FieldClass',
        ]


# Input Property
class InputProperty(Base):

    __tablename__ = "InputProperty"

    pk_InputProperty = Column(BigInteger, primary_key=True)

    fk_Input         = Column(ForeignKey('Input.pk_Input'), nullable=False)

    Name             = Column(String(255, 'French_CI_AS'), nullable=False)
    Value            = Column(String(255, 'French_CI_AS'), nullable=False)
    CreationDate     = Column(DateTime, nullable=False)
    ValueType        = Column(String(10, 'French_CI_AS'), nullable=False)

    Input = relationship('Input')

     # constructor
    def __init__(self, Name, Value, ValueType):
        self.Name         = Name
        self.Value        = Value
        self.ValueType    = ValueType
        self.CreationDate = datetime.datetime.now()

    # Return value casted on the correct format
    def getValue(self): 
        if self.ValueType == "Boolean":
            return bool(self.Value)
        elif self.ValueType == "Number":
            return int(self.Value)
        elif self.ValueType == "Double":
            return float(int(self.Value))
        else:
            return self.Value


# Configurated input
# A configurated input cans have one or more property
class ConfiguratedInput(Base):

    __tablename__ = 'ConfiguratedInput'

    pk_ConfiguratedInput = Column(BigInteger, primary_key=True)

    Name                 = Column(String(100, 'French_CI_AS'), nullable=False)
    LabelFR              = Column(String(300, 'French_CI_AS'), nullable=False)
    LabelEN              = Column(String(300, 'French_CI_AS'), nullable=False)
    IsRequired           = Column(BIT, nullable=False)
    IsReadOnly           = Column(BIT, nullable=False)
    FieldSize            = Column(String(100, 'French_CI_AS'), nullable=False)
    IsEOL                = Column(BIT, nullable=False)
    StartDate            = Column(DateTime, nullable=False)
    CurStatus            = Column(Integer, nullable=False)
    InputType            = Column(String(100, 'French_CI_AS'), nullable=False)
    EditorClass          = Column(String(100, 'French_CI_AS'), nullable=True)
    FieldClass           = Column(String(100, 'French_CI_AS'), nullable=True)

    Properties          = relationship("ConfiguratedInputProperty")

    # constructor
    def __init__(self, Name, LabelFR, LabelEN, IsRequired, IsReadOnly, FieldSize, IsEOL, InputType, EditorClass, FieldClass):
        self.Name        = Name
        self.LabelFR     = LabelFR
        self.LabelEN     = LabelEN
        self.IsRequired  = IsRequired
        self.IsReadOnly  = IsReadOnly
        self.FieldSize   = FieldSize
        self.IsEOL       = IsEOL
        self.InputType   = InputType
        self.EditorClass = EditorClass
        self.FieldClass  = FieldClass
        self.CurStatus  = "1"

        self.StartDate = datetime.datetime.now()

    # Return convert object to JSON object
    def toJSON(self):
        JSONObject = { 
            "LabelFR"     : self.LabelFR.decode('latin-1').encode("utf-8"),
            "LabelEN"     : self.LabelEN,
            "IsRequired"  : self.IsRequired,
            "IsEOL"       : self.IsEOL,
            "IsReadOnly"  : self.IsReadOnly,
            "FieldSize"   : self.FieldSize,
            "EditorClass" : self.EditorClass,
            "FieldClass"  : self.FieldClass,
            "InputType"   : self.InputType
        }

        for prop in self.Properties:
            JSONObject[prop.Name] = prop.getValue()

        return JSONObject

    # add property to the configurated input
    def addProperty(self, prop):
        self.Properties.append(prop)

    # get Column list except primary key and managed field like curStatus and StartDate
    @classmethod
    def getColumnsList(cls):
        return [
            'Name',
            'LabelFR',
            'LabelEN',
            'IsRequired',
            'IsReadOnly',
            'FieldSize',
            'IsEOL',
            'InputType',
            'EditorClass',
            'FieldClass',
        ]


# Configurated input property
class ConfiguratedInputProperty(Base):
    __tablename__ = 'ConfiguratedInputProperty'

    pk_ConfiguratedInputProperty = Column(BigInteger, primary_key=True)

    fk_ConfiguratedInput         = Column(ForeignKey('ConfiguratedInput.pk_ConfiguratedInput'), nullable=False)

    Name                         = Column(String(255, 'French_CI_AS'), nullable=False)
    Value                        = Column(String(255, 'French_CI_AS'), nullable=False)
    CreationDate                 = Column(DateTime, nullable=False)
    ValueType                    = Column(String(10, 'French_CI_AS'), nullable=False)

    ConfiguratedInput = relationship('ConfiguratedInput')

    # constructor
    def __init__(self, Name, Value, ValueType):
        self.Name         = Name
        self.Value        = Value
        self.ValueType    = ValueType
        self.CreationDate = datetime.datetime.now()

    # Return value casted on the correct format
    def getValue(self): 
        if self.ValueType == "Boolean":
            return bool(self.Value)
        elif self.ValueType == "Number":
            return int(self.Value)
        elif self.ValueType == "Double":
            return float(int(self.Value))
        else:
            return self.Value


# Database connexion
# We use pyodbc and SQL Server for the moment
engine = create_engine('mssql+pyodbc://CORLEONE-PC/formbuilder')

Base.metadata.create_all(engine)

session = Session(engine)