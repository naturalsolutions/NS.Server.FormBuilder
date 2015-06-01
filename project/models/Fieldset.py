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

    Form = relationship('Form')

    def __init__(self, legend, fields, multiple):
        self.legend = legend
        self.fields = fields
        self.multiple = multiple

    def update(self, legend, fields, multiple):
        self.legend = legend
        self.fields = fields
        self.multiple = multiple

    def toJSON(self):
        return {
            "legend": self.legend,
            "Fields": self.fields.split(',')
        }

    @classmethod
    def getColumnsList(cls):
        return [
            "legend",
            "fields",
            "multiple"
        ]