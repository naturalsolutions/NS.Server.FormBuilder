from sqlalchemy             import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm         import Session, relationship, backref
import datetime

# Get class from database
# See database-scripts folder to check database SQL schema
Base = automap_base()

# Form class
# Form has 0 or n Keywords 
class Form(Base):
    __tablename__ = 'Form'

    # Many to Many relations with KeyWord entity trhough KeyWord_Form relationship
    keywords        = relationship("KeyWord_Form", backref="protocol")

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
            "Keywords"      : keywords
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

    KeyWord         = relationship("KeyWord")

    #   Constructor
    def __init__(self):
        self.CreationDate = datetime.datetime.now()
        self.ModifDate = datetime.datetime.now()
        self.CurStatus = "1"

    # JSON serialization
    def serialize(self):
        return self.keyword.toJSON()


# Unity Class
class Unity(Base) :

    __tablename__ = "Unity"

    def toJSON(self):
        return {
            "ID"        : self.pk_Unity,
            "Name"      : self.Name,
            "LabelFR"   : self.LabelFR,
            "LabelEN"   : self.LabelEN
        }


# Database connexion
# We use pyodbc and SQL Server for the moment
engine = create_engine('mssql+pyodbc://CORLEONE-PC/formbuilder')
Base.prepare(engine, reflect=True)

session = Session(engine)