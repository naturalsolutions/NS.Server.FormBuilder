# -*- coding: utf8 -*-

from sqlalchemy import *
from .base import Base

# Propagation Class
class Propagation(Base):

    __tablename__   = "Propagation"

    Pk_ID           = Column(BigInteger, primary_key=True, nullable=False)
    FB_ID           = Column(BigInteger, nullable=True)
    Source_ID       = Column(BigInteger, nullable=False)
    Instance        = Column(String(100, 'French_CI_AS'), nullable=False)   
    TypeObject      = Column(String(100, 'French_CI_AS'), nullable=False)
    Priority        = Column(Integer, nullable=False)
    Propagation     = Column(Integer, nullable=False)
    Date_Modif      = Column(DateTime, nullable=True)
    Comment         = Column(String(500, 'French_CI_AS'), nullable=True)    

    def toJSON(self):
        return {
            "Pk_ID"         : self.Pk_ID,
            "FB_ID"         : self.FB_ID,
            "Source_ID"     : self.Source_ID,
            "Instance"      : self.Instance,
            "TypeObject"    : self.TypeObject,
            "Priority"      : self.Priority,
            "Propagation"   : self.Propagation,
            "Date_Modif"    : self.Date_Modif,
            "Comment"       : self.Comment
        }