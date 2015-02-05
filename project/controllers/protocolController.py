# -*- coding: utf-8 -*-
from project                import app
from flask                  import jsonify, abort, render_template, request, make_response
from ..models               import session, Form, KeyWord, Unity, ConfiguratedInput, ConfiguratedInputProperty, Input, InputProperty
from ..models.InputRepository import InputRepository
from ..utilities import Utility
import ConfigParser
import urllib2

import os
import sys
import datetime
import pprint
import json


pp = pprint.PrettyPrinter(indent=4)

#   Return all unit values
@app.route('/unities', methods = ['GET'])
def getUnities():
    unities = session.query(Unity).all()
    un   = []
    for each in unities:
        un.append( each.toJSON() )
    return jsonify ({ "options" : un })



# Return all forms
@app.route('/forms', methods = ['GET'])
def getForms():
    allForms            = session.query(Form).all()
    returnedFormsList   = []
    for each in allForms :
        returnedFormsList.append( each.toJSON() )

    return jsonify({ "options" : returnedFormsList})


# return all keywords
@app.route('/keywords', methods = ['GET'])
def getKeywords():
    keywords = session.query(KeyWord).all()
    ks   = []
    for each in keywords:
        ks.append( each.toJSON() )
    return jsonify ({ "options" : ks })


# Get protocol by ID
@app.route('/form/<formID>', methods = ['GET'])
def getFormByID(formID):
    findForm = session.query(Form).filter_by(pk_Form = formID)
    if findForm.count() > 0:
        return jsonify({ "form" : findForm.one().toJSON() })
    else:
        abort (404, 'No form found')


# Create form
@app.route('/form', methods = ['POST'])
def createForm():

    if request.json:
        #   Check if all parameters are present
        IfmissingParameters = True

        neededParametersList = Form.getColumnList()

        for a in neededParametersList : IfmissingParameters = IfmissingParameters and (a in request.json)

        if IfmissingParameters == False:
            abort(make_response('Some parameters are missing', 400))

        else:
            form            = Form(**request.json)              # new form Object
            inputColumnList = Input.getColumnsList()            # common input list like LabelFR, LabelEN see Input class

            # for each element in Schema we create an input and its properties
            for input in request.json['Schema']:
                inputsList              = request.json['Schema'][input]

                newInputValues          = Utility._pick(inputsList, inputColumnList)        # new input values
                newPropertiesValues     = Utility._pickNot(inputsList, inputColumnList)     # properties values
                newInput                = Input( **newInputValues )                         # new Input object

                # Add properties to the new configurated field
                for prop in newPropertiesValues:
                    property = InputProperty(prop, newPropertiesValues[prop], Utility._getType(newPropertiesValues[prop]))
                    newInput.addProperty(property)

                # Add new input to the form
                form.addInput(newInput)

            form.addKeywords( request.json['KeywordsFR'], 'FR' )
            form.addKeywords( request.json['KeywordsEN'], 'EN' )

            try:
                session.add (form)
                session.commit ()
                return jsonify({"form" : form.toJSON() })
            except:
                session.rollback()
                print( sys.exc_info() )
                abort(make_response('Error during save', 500))

    else:
        print("hein")
        abort(make_response('Data seems not be in JSON format', 400))


# PUT routes, update protocol
@app.route('/form/<int:id>', methods=['PUT'])
def updateForm(id):
    if request.json:

        IfmissingParameters = True

        neededParametersList = Form.getColumnList()

        for a in neededParametersList : IfmissingParameters = IfmissingParameters and (a in request.json)

        if IfmissingParameters == False:
            abort(make_response('Some parameters are missing', 400))

        else:
            form = session.query(Form).filter_by(pk_Form = id).first()
            if form != None:

                # Get form input ID list
                presentInputs = form.getInputsIdList()

                # We check if input in JSON data are yet present in the form
                # Yes : we update input
                # No : we add an input to the form
                for eachInput in request.json['Schema']:


                    if request.json['Schema'][eachInput]['ID'] in presentInputs:

                        # the field is present we update it
                        foundInput        = session.query(Input).filter_by(pk_Input = request.json['Schema'][eachInput]['ID']).first()
                        inputRepository   = InputRepository(foundInput)

                        inputNewValues    = request.json['Schema'][eachInput]

                        foundInputUpdated = inputRepository.updateInput(**inputNewValues)

                        presentInputs.remove(foundInput.pk_Input)

                    else:
                        inputRepository   = InputRepository(None)
                        # Add a new input to the form
                        form.addInput( inputRepository.createInput(**request.json['Schema'][eachInput]) )


                if len(presentInputs) > 0:
                    # We need to remove some input
                    inputRepository   = InputRepository(None)
                    inputRepository.removeInputs(presentInputs)

                #form.addKeywords( request.json['keywords'] )

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
    configuratedInputs        = {}
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

@app.route('/linked', methods = ['GET'])
def getLinkedFields():
    Config = ConfigParser.ConfigParser()
    Config.read("project/config/config.ini")

    linkedFieldsList = []
    # Get all webServices link
    for each in Config.options("webServices"):
        try:
            url     = Config.get("webServices", each)
            content = urllib2.urlopen(url, timeout = 1).read()

            # For each request we add the linked fields at the list
            linkedFieldsList = linkedFieldsList + json.loads(content)
        except urllib2.URLError, e:
            pass

    return jsonify({"linkedFields" : linkedFieldsList})

# Return main page, does nothing for the moment we prefer use web services
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')
