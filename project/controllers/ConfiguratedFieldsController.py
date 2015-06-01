# -*- coding: utf-8 -*-
# 
from project import app
from flask import jsonify, request, make_response, abort
from ..models import session
from ..models.ConfiguratedInput import ConfiguratedInput
from ..models.ConfiguratedInputProperty import ConfiguratedInputProperty
from ..utilities import Utility
import pprint

# GET, returns all configurated fields
@app.route('/configurations', methods = ['GET'])
def getConfiguration():
    configuratedInputsList    = session.query(ConfiguratedInput).all()
    configuratedInputs        = {}
    for each in configuratedInputsList :
        configuratedInputs[each.name] = each.toJSON()

    return jsonify({ "options" : configuratedInputs})


# User want to save a input as a configurated input
@app.route('/configurations', methods = ['POST'])
def createConfiguratedField():

    if 'field' not in request.json:
        abort(make_response('Some parameters are missing', 400))
    else:
        try:
            # Configurated input values
            # Main attributes like 'Name', 'LabelFR' or 'FieldSize' ...
            newConfiguratedInputValues  = Utility._pick(request.json['field'], ConfiguratedInput.getColumnsList())
            # Configurated input properties values
            # E.G : for a text input we have 'help', 'size' and 'defaultValue' ...
            newPropertiesValues         = Utility._pickNot(request.json['field'], ConfiguratedInput.getColumnsList())
            # New Configurated input object
            newConfiguratedField        = ConfiguratedInput( **newConfiguratedInputValues )

            # Add properties to the new configurated field
            for prop in newPropertiesValues:
                property = ConfiguratedInputProperty(prop, newPropertiesValues[prop], Utility._getType(newPropertiesValues[prop]))
                newConfiguratedField.addProperty(property)

            try:
                session.add (newConfiguratedField)
                session.commit ()
                return jsonify({ "result" : True})
            except:                
                session.rollback()
                return jsonify({ "result" : False})

        except Exception as e:
            print (e.args)
            abort(make_response('An error occurred, input not saved !', 500))