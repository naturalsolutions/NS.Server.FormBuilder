# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
import datetime


# Input Property
class InputProperty(Base):

    __tablename__ = "InputProperty"

    pk_InputProperty = Column(BigInteger, primary_key=True)

    fk_Input         = Column(ForeignKey('Input.pk_Input'), nullable=False)

    name             = Column(String(255, 'French_CI_AS'), nullable=False)
    value            = Column(String(5000, 'French_CI_AS'), nullable=False)
    creationDate     = Column(DateTime, nullable=False)
    valueType        = Column(String(10, 'French_CI_AS'), nullable=False)

    Input = relationship('Input')

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
                return self.value in ['true', 'yes', '1', 'True']
            elif self.valueType == "Number":
                return int(self.value)
            elif self.valueType == "Double":
                return float(int(self.value))
            else:
                return self.value
        except:
            return self.value