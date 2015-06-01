# -*- coding: utf8 -*-

from sqlalchemy import *
from .base import Base


# Unity Class
class Unity(Base):

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