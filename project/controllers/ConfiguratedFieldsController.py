# -*- coding: utf-8 -*-
# 
from project import app
from flask import jsonify, request, make_response, abort
from ..models import session
from ..models.ConfiguratedInput import ConfiguratedInput
from ..models.ConfiguratedInputProperty import ConfiguratedInputProperty
from ..utilities import Utility
import pprint
import json

# GET, returns all configurated fields
@app.route('/configurations', methods = ['GET'])
def getConfiguration():
    configuratedInputsList    = session.query(ConfiguratedInput).all()
    configuratedInputs        = {}
    for each in configuratedInputsList :
        configuratedInputs[each.name] = each.toJSON()

    return jsonify({ "options" : configuratedInputs})



# GET, returns one configurated field
@app.route('/configurations/<string:fieldName>', methods=['GET'])
def getOneConfiguration(fieldName):
    configuratedInputsList = session.query(ConfiguratedInput).filter_by(name = fieldName).all()
    configuratedInputs        = {}
    items = 0
    for each in configuratedInputsList:
        configuratedInputs[items] = each.toJSON()
        items = items + 1

    return jsonify({ "result" : configuratedInputs[0]})

# User want to save a input as a configurated input
@app.route('/configurations', methods = ['POST'])
def createConfiguratedField():

    if 'field' not in request.json:
        abort(make_response('Some parameters are missing', 400))
    else:
        # Configurated input values
        # Main attributes like 'Name', 'LabelFR' or 'FieldSize' ...
        newConfiguratedInputValues  = Utility._pick(request.json['field'], ConfiguratedInput.getColumnsList())
        # Configurated input properties values
        # E.G : for a text input we have 'help', 'size' and 'defaultValue' ...
        newPropertiesValues         = Utility._pickNot(request.json['field'], ConfiguratedInput.getColumnsList())

        configuratedInput = session.query(ConfiguratedInput).filter_by(name = newConfiguratedInputValues["name"]).first()

        if (configuratedInput != None):
            session.query(ConfiguratedInputProperty).filter_by(fk_ConfiguratedInput = configuratedInput.pk_ConfiguratedInput).delete()
            session.query(ConfiguratedInput).filter_by(name = newConfiguratedInputValues["name"]).delete()

        # New Configurated input object
        newConfiguratedField        = ConfiguratedInput( **newConfiguratedInputValues )

        # Add properties to the new configurated field
        for prop in newPropertiesValues :
            if newPropertiesValues[prop] == None :
                newPropertiesValues[prop] = ''
            property = ConfiguratedInputProperty(prop, newPropertiesValues[prop], Utility._getType(newPropertiesValues[prop]))
            newConfiguratedField.addProperty(property)

        try:
            session.add (newConfiguratedField)
            session.commit()
            return jsonify({ "result" : True})
        except:                
            session.rollback()
            return jsonify({ "result" : False})
            