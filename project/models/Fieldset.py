# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base


class Fieldset(Base):

    __tablename__ = 'Fieldset'

    pk_Fieldset = Column(BigInteger, primary_key=True)

    fk_form = Column(ForeignKey('Form.pk_Form'), nullable=False)

    legend = Column(String(255, 'French_CI_AS'), nullable=False)
    fields = Column(String(255, 'French_CI_AS'), nullable=False)
    multiple = Column(Boolean, nullable=True)
    curStatus = Column(Integer, nullable=False)
    refid = Column(String(255, 'French_CI_AS'), nullable=False)

    Form = relationship('Form')

    def __init__(self, legend, fields, multiple, refid):
        self.legend = legend
        self.fields = fields
        self.multiple = multiple
        self.curStatus = 0
        self.refid = refid

    def update(self, legend, fields, multiple, refid):
        self.legend = legend
        self.fields = fields
        self.multiple = multiple
        self.refid = refid

    def toJSON(self):
        return {
            "legend"    : self.legend,
            "fields"    : self.fields.split(',') if len(self.fields)> 0 else [],
            "multiple"    : self.multiple,
            "refid"    : self.refid
        }

    @classmethod
    def getColumnsList(cls):
        return [
            "legend",
            "fields",
            "multiple",
            "refid"
        ]