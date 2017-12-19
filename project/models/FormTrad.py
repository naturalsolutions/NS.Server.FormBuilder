# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base


class FormTrad(Base):

    __tablename__ = 'FormTrad'

    pk_FormTrad = Column(BigInteger, primary_key=True)
    fk_Form = Column(ForeignKey('Form.pk_Form'), nullable=False)
    fk_Language = Column(ForeignKey('Language.pk_Name'), nullable=False)

    Name = Column(String(255, 'French_CI_AS'), nullable=False)
    Description = Column(String(300, 'French_CI_AS'))
    Keywords = Column(String(300, 'French_CI_AS'))

    Form = relationship('Form')

    def __init__(self, Language, Name='', Description='', Keywords=''):
        self.fk_Language = Language
        self.Name = Name
        self.Description = Description
        self.Keywords = Keywords

    def update(self, Language, Name='', Description='', Keywords=''):
        self.fk_Language = Language
        self.Name = Name
        self.Description = Description
        self.Keywords = Keywords

    def toJSON(self):
        return {
            "Language": self.fk_Language,
            "Name": self.Name,
            "Description": self.Description,
            "Keywords": self.Keywords
        }

    @classmethod
    def getColumnsList(cls):
        return [
            "Language",
            "Name",
            "Description",
            "Keywords"
        ]
