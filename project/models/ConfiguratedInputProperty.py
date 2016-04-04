# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
import datetime


# Configurated input property
class ConfiguratedInputProperty(Base):
    __tablename__ = 'ConfiguratedInputProperty'

    pk_ConfiguratedInputProperty = Column(BigInteger, primary_key=True)

    fk_ConfiguratedInput         = Column(ForeignKey('ConfiguratedInput.pk_ConfiguratedInput'), nullable=False)

    name                         = Column(String(255, ''), nullable=False)
    value                        = Column(String(5000, 'French_CI_AS'), nullable=False)
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