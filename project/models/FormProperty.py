# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
import datetime


# Form Property
class FormProperty(Base):

    __tablename__    = 'FormProperty'

    pk_FormProperty  = Column(BigInteger, primary_key=True)

    fk_Form          = Column(ForeignKey('Form.pk_Form'), nullable=False)

    name             = Column(String(255, 'French_CI_AS'), nullable=False)
    value            = Column(String(255, 'French_CI_AS'), nullable=False)
    creationDate     = Column(DateTime, nullable=False)
    valueType        = Column(String(10, 'French_CI_AS'), nullable=False)

    Form = relationship('Form')

    # Constructor
    def __init__(self, name, value, valueType):
        self.name         = name
        self.value        = value
        self.valueType    = valueType
        self.creationDate = datetime.datetime.now()

    # Return value casted on the correct format
    def getvalue(self):
        try:
            if self.valueType == "Boolean":
                return bool(self.value)
            elif self.valueType == "Number":
                return int(self.value)
            elif self.valueType == "Double":
                return float(int(self.value))
            else:
                return self.value
        except:
            return self.value

    def update(self, newName, newValue, newCreationDate, newValueType):
        print(newName)
        print(newValue)
        print(newCreationDate)
        print(newValueType)
        print("OLE OLE OLE OLEOLE OLE OLE OLEOLE OLE OLE OLEOLE OLE OLE OLEOLE OLE OLE OLEOLE OLE OLE OLE")
        self.name           = newName
        self.value          = newValue
        self.creationDate   = newCreationDate
        self.valueType      = newValueType