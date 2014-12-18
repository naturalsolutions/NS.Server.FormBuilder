# -*- coding: utf-8 -*-
from project                import app
from flask                  import jsonify, abort, render_template, request, make_response
from ..models               import session, Form, KeyWord, Unity, ConfiguratedInput, ConfiguratedInputProperty, Input, InputProperty
from ..utilities import Utility

import os
import sys
import datetime
import pprint

pp = pprint.PrettyPrinter(indent=4)

#   ---------------------------------------------------------
#   Return all unit values
@app.route('/unities', methods = ['GET'])
def getUnities():
    unities = session.query(Unity).all()
    un   = []
    for each in unities:
        un.append( each.toJSON() )
    return jsonify ({ "options" : un })


#   --------------------------------------------------------
# Return a list of protocols name
# Used for javascript autocomplete source
@app.route('/forms', methods = ['GET'])
def getProtocols():
    protos      = session.query(Form).all()
    protocols   = []
    for each in protos :
        protocols.append( each.toJSON() )
    return jsonify({ "options" : protocols})


#   --------------------------------------------------------
# return a list a keyword values
# Used for javascript autocomplete source
@app.route('/keywords', methods = ['GET'])
def getKeywords():
    keywords = session.query(KeyWord).all()
    ks   = []
    for each in keywords:
        ks.append( each.toJSON() )
    return jsonify ({ "options" : ks })


#   --------------------------------------------------------
# Get protocol by name
@app.route('/forms/<formName>', methods = ['GET'])
def getProtocolsByName(formName):
    forms = session.query(Form).filter_by(Name = formName)
    if forms.count() > 0:
        return jsonify({ formName : forms.one().toJSON() })
    else:
        abort (404, 'Form found for this name')


#   -------------------------------------------------------
# POST routes, create a form with name and content
@app.route('/form', methods = ['POST'])
def createProtocole():

    if request.json:

        #   Check if all parameters are present
        IfmissingParameters = True

        neededParametersList = [
            'Name',
            'Comment',
            'Keywords',
            'LabelFR',
            'LabelEN',
            'Schema',
            'Fieldsets'
        ]

        for a in neededParametersList : IfmissingParameters = IfmissingParameters and (a in request.json)

        if IfmissingParameters == False:

            abort(make_response('Some parameters are missing', 400))

        else:
            form = Form(**request.json)

            # for each element in Schema we create an input and its properties
            for input in request.json['Schema']:
                # new input values
                newInputValues              = Utility._pick(request.json['Schema'][input], Input.getColumnsList())
                # properties values
                newPropertiesValues         = Utility._pickNot(request.json['Schema'][input], Input.getColumnsList())
                # new Input object
                newInput                    = Input( **newInputValues )
                # Add properties to the new configurated field
                for prop in newPropertiesValues:
                    property = InputProperty(prop, newPropertiesValues[prop], Utility._getType(newPropertiesValues[prop]))
                    newInput.addProperty(property)

                # Add new input to the form
                form.addInput(newInput)

            form.addKeywords( request.json['Keywords'] )
            try:
                session.add (form)
                session.commit ()
                return jsonify({"form" : form.toJSON() })
            except:
                session.rollback()
                print( sys.exc_info() )
                abort(make_response('Error during save', 500))

    else:
        abort(make_response('Data seems not be in JSON format', 400))


# PUT routes, update protocol
@app.route('/protocols/<int:id>', methods=['PUT'])
def updateProtocol(id):
    if request.json:
        IfmissingParameters     = True
        neededParametersList    = [
            'name',
            'description',
            'keywords',
            'labelFr',
            'labelEn',
            'schema',
            'fieldsets'
        ]

        for a in neededParametersList:
            IfmissingParameters = IfmissingParameters and (a in request.json)

        if IfmissingParameters == False:

            abort(make_response('Some parameters are missing', 400))

        else:
            form = self._session.query(Protocol).filter(Protocol.id == id).first()
            if form != None:

                form.Name      = request.json['name']
                form.labelFR   = request.json['labelFr']
                form.labelEN   = request.json['labelEn']
                form.comment   = request.json['description']
                form.ModifDate = datetime.datetime.now()

                form.addKeywords( request.json['keywords'] )

                try:
                    session.add (form)
                    session.commit ()
                    return jsonify({"form" : form.toJSON() })
                except:
                    session.rollback()
                    print( sys.exc_info() )
                    abort(make_response('Error', 500))

            else:
                abort(make_response('No form found with this ID', 404))

    else:
        abort(make_response('Data seems not be in ' + format +' format', 400))

# GET, returns all configurated fields
@app.route('/configurations', methods = ['GET'])
def getConfiguration():
    configuratedInputsList    = session.query(ConfiguratedInput).all()
    configuratedInputs   = {}

    for each in configuratedInputsList :
        configuratedInputs[each.Name] = each.toJSON()

    return jsonify({ "options" : configuratedInputs})


# User want to save a input as a configurated input
@app.route('/configurations', methods = ['POST'])
def createConfiguratedField():

    if not request.json:
        abort(make_response('Data seems not be in JSON format', 400))
    elif not 'field' in request.json:
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
                print "Unexpected error:", sys.exc_info()[0]
                return jsonify({ "result" : False})

        except:
            abort(make_response('An error occured, input not saved !', 500))


@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')
