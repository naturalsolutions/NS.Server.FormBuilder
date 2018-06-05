# -*- coding: utf8 -*-
from sqlalchemy import *
from sqlalchemy.orm import relationship
from .base import Base
from ..models.InputTrad import InputTrad
import datetime
import json
from ..utilities import EditMode
from collections import OrderedDict


# Input Class
class Input(Base):

    __tablename__ = "Input"

    pk_Input      = Column(BigInteger, primary_key=True)

    fk_form       = Column(ForeignKey('Form.pk_Form'), nullable=False)

    name          = Column(String(100, 'French_CI_AS'), nullable=False)
    # labelFr       = Column(String(300, 'French_CI_AS'), nullable=False)
    # labelEn       = Column(String(300, 'French_CI_AS'), nullable=False)
    editMode      = Column(Integer, nullable=False)
    fieldSize     = Column(String(100, 'French_CI_AS'), nullable=False)
    atBeginingOfLine = Column(Boolean, nullable=False)
    startDate     = Column(DateTime, nullable=False)
    curStatus     = Column(Integer, nullable=False)
    order         = Column(SmallInteger, nullable=True)
    type          = Column(String(100, 'French_CI_AS'), nullable=False)
    editorClass   = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClassEdit    = Column(String(100, 'French_CI_AS'), nullable=True)
    fieldClassDisplay    = Column(String(100, 'French_CI_AS'), nullable=True)
    originalID              = Column(BigInteger, nullable=True)
    
    # linked field section
    linkedFieldTable             = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedField                  = Column(String(100, 'French_CI_AS'), nullable=True)
    linkedFieldset               = Column(String(100, 'French_CI_AS'), nullable=True)

    Form        = relationship('Form')
    Properties  = relationship("InputProperty", cascade="all")
    InputTrad   = relationship("InputTrad", cascade="all", lazy="dynamic")

    # constructor
    def __init__(self, name, translations, editMode, fieldSize, atBeginingOfLine, type, editorClass, fieldClassEdit, fieldClassDisplay, linkedFieldTable, linkedField, linkedFieldset, order, originalID):
        self.name           = name
        self.addTranslations(translations)
        self.editMode       = editMode
        self.fieldSize      = fieldSize
        self.atBeginingOfLine = atBeginingOfLine
        self.type           = type
        self.editorClass    = editorClass
        self.fieldClassEdit     = fieldClassEdit
        self.fieldClassDisplay     = fieldClassDisplay
        self.linkedField    = linkedField
        self.curStatus      = "1"
        self.order          = order
        self.originalID     = originalID

        # linked field
        self.linkedFieldTable             = linkedFieldTable
        self.linkedField                  = linkedField
        self.linkedFieldset               = linkedFieldset

        self.startDate = datetime.datetime.now()

    # Update form values
    def update(self, **kwargs):
        self.name        = kwargs['name']
        self.editMode    = kwargs['editMode']
        self.fieldSize   = kwargs['fieldSize']
        self.atBeginingOfLine   = kwargs['atBeginingOfLine']
        self.editorClass = kwargs['editorClass']
        self.fieldClassEdit  = kwargs['fieldClassEdit']
        self.fieldClassDisplay  = kwargs['fieldClassDisplay']
        self.order       = kwargs['order']
        self.originalID = kwargs['originalID']
        self.addTranslations(kwargs['translations'])

        # linked field
        self.linkedFieldTable             = kwargs['linkedFieldTable']
        self.linkedField                  = kwargs['linkedField']
        self.linkedFieldset               = kwargs['linkedFieldset']

    # Return convert object to JSON object
    def toJSON(self):
        JSONObject = {
            "id"                : self.pk_Input,
            "atBeginingOfLine"  : self.atBeginingOfLine,
            "editMode"          : self.editMode,
            "fieldSize"         : self.fieldSize,
            "editorClass"       : self.editorClass,
            "fieldClassEdit"    : self.fieldClassEdit,
            "fieldClassDisplay" : self.fieldClassDisplay,
            "originalID"        : self.originalID,
            "type"              : self.type,
            "order"             : self.order,
            "name"              : self.name,
            "linkedFieldset"    : self.linkedFieldset,

            # linked field 

            "linkedFieldTable"             : self.linkedFieldTable,
            "linkedField"                  : self.linkedField,

            "translations"  : self.getTranslations()
        }

        for prop in self.Properties :
            JSONObject[prop.name] = prop.getvalue()

        #TODO Find out why this exists ?
        #if (self.type == 'ChildForm') :
        #    JSONObject[realChildFormName] = 

        return JSONObject

    def toJSONSchema(self, session, FormClass):
        """
        :param session: (circular import) used to populate child form schema
        :param FormClass: (circular import) used to populate child form schema
        :return:
        """
        s = OrderedDict([
          ("title", self.name),
          ("fbType", self.type),
          ("translations", self.getTranslations()),
        ])

        # map formbuilder type to concrete json-schema type
        typesMap = {
            "Autocomplete": "string",
            "AutocompleteTreeView": "integer", # todo ?
            "Checkboxes": "array",
            "ChildForm": "object",
            "Date": "string",
            "Decimal": "number",
            "File": "string", # todo ?
            "Number": "number",
            "NumericRange": "number",
            "ObjectPicker": "integer", # todo ?
            "Pattern": "string", # todo ?
            "Position": "integer", # todo ?
            "Radio": "string",
            "Select": "string",
            "SubFormGrid": "object",
            "TextArea": "string",
            "Text": "string",
            "Thesaurus": "integer", # todo ?
            "TreeView": "integer", # todo ?
        }
        s["type"] = typesMap[self.type]

        # default
        if self.getProperty("defaultValue") != "":
            s["default"] = self.getProperty("defaultValue")

        # numeric's minimum & maximum
        if s["type"] in ["integer", "number"]:
            minVal = self.getProperty("minValue")
            maxVal = self.getProperty("maxValue")
            if minVal:
                try:
                    s["minimum"] = float(minVal) if s["type"] == "integer" else int(minVal)
                except:
                    pass
            if maxVal:
                try:
                    s["maximum"] = float(maxVal) if s["type"] == "integer" else int(maxVal)
                except:
                    pass

        # child form: populate sub-schema
        if s["fbType"] in ["ChildForm", "SubFormGrid"]:
            try:
                subForm = session.query(FormClass).get(int(self.getProperty("childForm")))
                if EditMode(self.editMode).nullable:
                    s["anyOf"] = [subForm.toJSONSchema(session), {}]
                else:
                    s["allOf"] = [subForm.toJSONSchema(session)]
            except Exception as e:
                raise Exception("couldn't populate child form schema", e)

        # date format
        if s["fbType"] == "Date":
            # todo we could use "pattern": "date | <regexp> | .." keyword from json-schema spec,
            # but it would need to match the spec whereas our "format" is not standard
            s["format"] = self.getProperty("format")

        # choices types: "Radio", "Select" and "Checkboxes"
        if s["fbType"] == "Radio" or s["fbType"] == "Select" or s["fbType"] == "Checkboxes":
            try:
                choices = json.loads(self.getProperty("choices"))
            except:
                # non fatal error but there will be no restriction on value for this field
                print("error parsing choices for %s field: \"%s\"" % (s["fbType"], self.name))
                choices = []
            enumValues = []
            defaultValues = []
            for choice in choices:
                enumValues.append(choice["value"])
                if "isDefaultValue" in choice and choice["isDefaultValue"]:
                    defaultValues.append(choice["value"])

            # "Checkboxes"
            if s["type"] == "array":
                if defaultValues:
                    s["default"] = defaultValues
                if enumValues:
                    s["items"] = {"enum": enumValues}
            # "Radio", "Select" - single value
            else:
                if defaultValues:
                    s["default"] = defaultValues[0] # only keep first default choice
                if enumValues:
                    s["enum"] = enumValues

        # editMode
        editMode = EditMode(self.editMode)
        if not editMode.editable:
            s["readOnly"] = True
        if not editMode.visible:
            s["hidden"] = True
        if editMode.nullmean or editMode.nullable:
            s["type"] = [s["type"], "null"]
            if "enum" in s:
                s["enum"].append("null")

        # set default if not populated before
        if not "default" in s and self.getProperty("defaultValue") != "":
            s["default"] = self.getProperty("defaultValue")

        # other static props of interest: todo ?
        if self.linkedField:
            s["linkedField"] = self.linkedField
        if self.linkedFieldTable:
            s["linkedFieldTable"] = self.linkedFieldTable
        if self.fieldSize:
            s["fieldSize"] = self.fieldSize
        s["atBeginingOfLine"] = self.atBeginingOfLine
        s["order"] = self.order

        # other dyn props encountered, maybe exhaustive, probably not: todo ?
        for dynProp in [
            "url", "wsUrl", "webservices", "webServiceURL",
            "isSQL", "isDefaultSQL",
            "defaultNode", "fullpath", "defaultPath", "positionPath"]:
            if self.getProperty(dynProp) != "":
                s[dynProp] = self.getProperty(dynProp)

        return s

    def addTranslations(self, translations):
        for lang in translations:
            if self.pk_Input:
                trad = self.InputTrad.filter_by(fk_Language = lang).first()
                if trad:
                    trad.update(**translations[lang])
                    continue

            self.InputTrad.append(InputTrad(**translations[lang]))

    # add property to the configurated input
    def addProperty(self, prop):
        self.Properties.append(prop)

    def getProperty(self, propname):
        for InputProp in self.Properties:
            if InputProp.name == propname:
                return InputProp.value
        return ""

    # get Column list except primary key and managed field like curStatus and startDate
    @classmethod
    def getColumnsList(cls):
        return [
            'name',
            'translations',
            'editMode',
            'fieldSize',
            'atBeginingOfLine',
            'type',
            'editorClass',
            'fieldClassEdit',
            'fieldClassDisplay',
            'linkedFieldTable',
            'linkedField',
            'linkedFieldset',
            'order',
            'originalID'
        ]

    def getTranslations(self):
        translations = dict()
        allTrad = self.InputTrad
        for each in allTrad:
            translations[each.fk_Language] = each.toJSON()
        return translations