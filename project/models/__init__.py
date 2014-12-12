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

    pk_Form      = Column(BigInteger, primary_key=True)

    Name         = Column(String(100, 'French_CI_AS'), nullable=False)
    LabelFR      = Column(String(300, 'French_CI_AS'), nullable=False)
    LabelEN      = Column(String(300, 'French_CI_AS'), nullable=False)
    CreationDate = Column(DateTime, nullable=False)
    ModifDate    = Column(DateTime, nullable=True)
    CurStatus    = Column(Integer, nullable=False)
    Comment      = Column(String(collation='French_CI_AS'), nullable=False)

    # Relationship
    keywords        = relationship("KeyWord_Form")  # A form has many Keywords
    inputs          = relationship("Input")         # A form has many Inputs

    # Constructor
    def __init__(self, name, LabelFR, LabelEN, Comment):
        self.Name         = name
        self.LabelFR      = LabelFR
        self.LabelEN      = LabelEN
        self.Comment      = Comment
        self.CreationDate = datetime.datetime.now()
        self.ModifDate    = datetime.datetime.now()
        self.CurStatus    = "1"

    # Serialize a form in JSON object
    def toJSON(self):
        inputs = []
        for each in self.inputs:
            inputs.append( each.toJSON() )
        keywords = []
        for each in self.keywords : 
            keywords.append (each.serialize())
        return {
            "ID"            : self.pk_Form,
            "Name"          : self.Name,
            "LabelFR"       : self.LabelFR,
            "LabelEN"       : self.LabelEN,
            "CreationDate"  : self.CreationDate,
            "ModifDate"     : self.ModifDate,
            "CurStatus"     : self.CurStatus,
            "Comment"       : self.Comment,
            "Keywords"      : keywords,
            "Schema"        : inputs
        }

    # Add keyword to the form
    def addKeywords(self, KeyWordList):
        for each in KeyWordList:
            a = KeyWord_Form()
            a.KeyWord = KeyWord(each)
            #a.Form = self
            self.keywords.append(a)


# KeyWord Class
# A Keyword can be used by many Form
class KeyWord(Base) :

    __tablename__ = 'KeyWord'

    pk_KeyWord   = Column(BigInteger, primary_key=True)
    Name         = Column(String(100, 'French_CI_AS'), nullable=False, unique=True)
    CreationDate = Column(DateTime, nullable=False)
    ModifDate    = Column(DateTime, nullable=True)
    CurStatus    = Column(Integer, nullable=False)

    # Constuctor
    def __init__(self, name):
        self.Name = name
        self.CreationDate = datetime.datetime.now()
        self.ModifDate = datetime.datetime.now()
        self.CurStatus = "1"

    # Serialize a KeyWord object in JSON format
    def toJSON(self):
        return {
            "ID"            : self.pk_KeyWord,
            "Name"          : self.Name,
            "CreationDate"  : self.CreationDate,
            "ModifDate"     : self.ModifDate,
            "CurStatus"     : self.CurStatus,
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
    def serialize(self):
        return self.KeyWord.toJSON()


# Unity Class
class Unity(Base) :

    __tablename__ = "Unity"

    pk_Unity = Column(BigInteger, primary_key=True)
    Name     = Column(BigInteger, nullable=False)
    LabelFR  = Column(String(300, 'French_CI_AS'))
    LabelEN  = Column(String(300, 'French_CI_AS'))

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
    BootStrapSize = Column(String(100, 'French_CI_AS'), nullable=False)
    IsEOL         = Column(BIT, nullable=False)
    StartDate     = Column(DateTime, nullable=False)
    CurStatus     = Column(Integer, nullable=False)
    InputType     = Column(String(100, 'French_CI_AS'), nullable=False)
    EditorClass   = Column(String(100, 'French_CI_AS'), nullable=True)
    FieldCLass    = Column(String(100, 'French_CI_AS'), nullable=True)
    
    Form = relationship('Form')

    def toJSON(self):
        return {
            "ID"        : self.pk_Input,
            "Name"      : self.Name,
            "LabelFR"   : self.LabelFR,
            "LabelEN"   : self.LabelEN
        }

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

    def toJSON(self):
        return {
        }


class ConfiguratedInput(Base):
    __tablename__ = 'ConfiguratedInput'

    pk_ConfiguratedInput = Column(BigInteger, primary_key=True)

    Name                 = Column(String(100, 'French_CI_AS'), nullable=False)
    LabelFR              = Column(String(300, 'French_CI_AS'), nullable=False)
    LabelEN              = Column(String(300, 'French_CI_AS'), nullable=False)
    IsRequired           = Column(BIT, nullable=False)
    IsReadOnly           = Column(BIT, nullable=False)
    BootStrapSize        = Column(String(100, 'French_CI_AS'), nullable=False)
    IsEOL                = Column(BIT, nullable=False)
    StartDate            = Column(DateTime, nullable=False)
    CurStatus            = Column(Integer, nullable=False)
    InputType            = Column(String(100, 'French_CI_AS'), nullable=False)
    EditorClass          = Column(String(100, 'French_CI_AS'), nullable=True)
    FieldCLass           = Column(String(100, 'French_CI_AS'), nullable=True)


class ConfiguratedInputProperty(Base):
    __tablename__ = 'ConfiguratedInputProperty'

    pk_ConfiguratedInputProperty = Column(BigInteger, primary_key=True)

    fk_ConfiguratedInput         = Column(ForeignKey('ConfiguratedInput.pk_ConfiguratedInput'), nullable=False)
    
    Name                         = Column(String(255, 'French_CI_AS'), nullable=False)
    Value                        = Column(String(255, 'French_CI_AS'), nullable=False)
    CreationDate                 = Column(DateTime, nullable=False)
    ValueType                    = Column(String(10, 'French_CI_AS'), nullable=False)

    ConfiguratedInput = relationship('ConfiguratedInput')

# Database connexion
# We use pyodbc and SQL Server for the moment
engine = create_engine('mssql+pyodbc://CORLEONE-PC/formbuilder')

Base.metadata.create_all(engine)

session = Session(engine)