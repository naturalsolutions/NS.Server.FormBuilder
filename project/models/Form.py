# -*- coding: utf8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
from ..utilities import Utility
from ..models.FormProperty import FormProperty
from ..models.FormTrad import FormTrad
from ..models.InputProperty import InputProperty
import datetime


class Form(Base):
    __tablename__ = 'Form'

    pk_Form = Column(BigInteger, primary_key=True)

    name = Column(String(100, 'French_CI_AS'), nullable=False, unique=True)
    tag = Column(String(300, 'French_CI_AS'), nullable=True)
    creationDate = Column(DateTime, nullable=False)
    modificationDate = Column(DateTime, nullable=True)
    curStatus = Column(Integer, nullable=False)
    obsolete = Column(Boolean, nullable=False)
    isTemplate = Column(Boolean, nullable=False)
    context = Column(String(50, 'French_CI_AS'), nullable=False)
    originalID = Column(Integer, nullable=True)
    propagate = Column(Boolean, nullable=False)
    state = Column(Integer, nullable=False)     # 1: current version, 2: old version, 3: current version (deleted)
    initialID = Column(Integer, nullable=False) # id of root form after first creation

    # Relationship
    inputs = relationship("Input", cascade="all")
    Properties = relationship("FormProperty", cascade="all")
    FormFile = relationship("FormFile", cascade="all")
    FormTrad = relationship("FormTrad", cascade="all", lazy='dynamic')

    # Constructor
    def __init__(self, **kwargs):
        """
        Constructor
        :param kwargs:dict Dicth with initialized values
        :return:
        """
        self.name = kwargs['name']
        self.addTranslations(kwargs['translations'])
        self.tag = kwargs['tag']
        self.creationDate = datetime.datetime.now()
        self.modificationDate = datetime.datetime.now()
        self.curStatus = "1"
        self.obsolete = kwargs['obsolete']
        self.isTemplate = kwargs['isTemplate']
        self.context = kwargs['context']
        self.propagate = kwargs['propagate']

    # Update form values
    def update(self, **kwargs):
        """
        Update form attributes with dict
        :param kwargs: dict
        :return:
        """
        self.name = kwargs['name']
        self.tag = kwargs['tag']
        self.modificationDate = datetime.datetime.now()
        self.isTemplate = kwargs['isTemplate']
        self.context = kwargs['context']
        self.propagate = kwargs['propagate']
        self.obsolete = kwargs['obsolete']
        self.addTranslations(kwargs['translations'])

    def get_formtrad(self):
        """
        Return all form trads
        :return: form trads as json
        """
        trads = []
        for each in self.FormTrad:
            trads.append(each.toJSON())
        return trads

    def to_json(self):
        """
        Return form as json without relationship
        :return: form as json without relationship
        """

        return {
            "id": self.pk_Form,
            "name": self.name,
            "tag": self.tag,
            "creationDate": Utility.datetimeToStr(self.creationDate),
            "modificationDate": Utility.datetimeToStr(self.modificationDate),
            "curStatus": self.curStatus,
            "obsolete": self.obsolete,
            "isTemplate": self.isTemplate,
            "context": self.context,
            "propagate": self.propagate,
            "originalID": self.originalID,
            "state": self.state,
            "initialID": self.initialID
        }

    # Serialize a form in JSON object
    def toJSON(self):
        json = self.to_json()
        json['translations'] = self.getTranslations()
        return json

    def addFormProperties(self, jsonobject):
        for prop in self.Properties:
            jsonobject[prop.name] = prop.getvalue()
        jsonobject['fileList'] = []
        for fileAssoc in self.FormFile:
            jsonobject['fileList'].append(fileAssoc.toJSON())
        return jsonobject

    def shortJSON(self):
        return {
            "id": self.pk_Form,
            "name": self.name,
            "context": self.context,
            "obsolete": self.obsolete,
            "modificationDate": Utility.datetimeToStr(self.modificationDate),
            "state": self.state,
            "initialID": self.initialID
        }

    def recuriseToJSON(self, withschema=True):
        json = self.toJSON()

        if withschema:
            json['schema'] = {}
            i = 0
            for each in self.inputs:
                json['schema'][i] = each.toJSON()
                i += 1

        json['translations'] = self.getTranslations()
        json = self.addFormProperties(json)
        return json

    def hasCircularDependencies(self, allParents, session):
        toret = true
        for FormInput in self.inputs:
            if FormInput.type == 'ChildForm':
                childFormName = FormInput.getProperty('childFormName')
                if childFormName in allParents:
                    return true
                else:
                    tempAllParents = allParents
                    tempAllParents.append(self.name)
                    SubForm = session.query(Form).filter_by(
                        name=childFormName).first()
                    toret = toret and (SubForm is None or not SubForm.hasCircularDependencies(
                        tempAllParents, session))
        return (not toret)

    #get translations from FormTrad
    def getTranslations(self):
        translations = dict()
        allTrad = self.FormTrad
        for each in allTrad:
            translations[each.fk_Language] = each.toJSON()
        return translations 
    
    # Add Input to the form
    def addInput(self, newInput):
        self.inputs.append(newInput)

    # Add FormFile to the form
    def addFile(self, newFile):
        self.FormFile.append(newFile)

    # return a list of all form's inputs id
    def getInputsIdList(self):
        inputsIdList = []
        for i in self.inputs:
            inputsIdList.append(i.pk_Input)
        return inputsIdList

    # get all forms referencing this form as a child
    def getParentForms(self, session):
        parents = []
        for childFormProp in session.query(InputProperty).filter_by(value = str(self.pk_Form), name = "childForm").all():
            parent = childFormProp.Input.Form
            if parent.state == 1:
                parents.append({
                    "id":   parent.pk_Form,
                    "name": parent.name
                })
        return parents

    # update all forms referencing this form as a child with provided newForm
    def updateParentForms(self, session, newForm):
        i = 0
        for childFormProp in session.query(InputProperty).filter_by(value = str(self.pk_Form), name = "childForm").all():
            for prop in childFormProp.Input.Properties:
                if prop.name == 'childForm':
                    prop.value = newForm.pk_Form
                elif prop.name == 'childFormName':
                    prop.value = newForm.name
            i += 1
            # todo trigger bridge update

        # commit session if changes were made
        if i > 0:
            session.commit()

        return i


    def addTranslations(self, translations):
        for lang in translations:
            if self.pk_Form:
                trad = self.FormTrad.filter_by(fk_Language = lang).first()
                if trad:
                    trad.update(**translations[lang])
                    continue

            self.FormTrad.append(FormTrad(**translations[lang]))

    def addProperty(self, prop):
        self.Properties.append(prop)

    def updateProperties(self, properties):
        for prop in properties:
            if properties[prop] == None:
                properties[prop] = ''
            formProperty = FormProperty(
                prop, properties[prop], Utility._getType(properties[prop]))
            self.updateProperty(formProperty)

    def updateProperty(self, prop):
        for formprop in self.Properties:
            if formprop.name == prop.name:
                formprop.update(prop.name, prop.value,
                                prop.creationDate, prop.valueType)
                break

    @classmethod
    def getColumnList(cls):
        return [
            'name',
            'tag',
            'translations',
            'schema',
            'obsolete',
            'isTemplate',
            'context',
            'propagate',
            'originalID',
            'initialID'
        ]
