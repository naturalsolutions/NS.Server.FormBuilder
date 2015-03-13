# -*- coding: utf-8 -*-
# 
from project                    import app
from flask                      import jsonify, abort, render_template, request, make_response
from ..models                   import session, Form, KeyWord, Unity, ConfiguratedInput, ConfiguratedInputProperty, Input, InputProperty
from ..models.InputRepository   import InputRepository
from ..utilities                import Utility

import datetime
import json
import sys

# Return all forms
@app.route('/forms', methods = ['GET'])
def getForms():
    allForms            = session.query(Form).all()
    returnedFormsList   = []
    for each in allForms :
        returnedFormsList.append( each.toJSON() )

    return json.dumps(returnedFormsList)

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
            for input in request.json['schema']:
                inputsList              = request.json['schema'][input]

                newInputValues          = Utility._pick(inputsList, inputColumnList)        # new input values
                newPropertiesValues     = Utility._pickNot(inputsList, inputColumnList)     # properties values
                newInput                = Input( **newInputValues )                         # new Input object

                # Add properties to the new configurated field
                for prop in newPropertiesValues:
                    property = InputProperty(prop, newPropertiesValues[prop], Utility._getType(newPropertiesValues[prop]))
                    newInput.addProperty(property)

                # Add new input to the form
                form.addInput(newInput)

            form.addKeywords( request.json['keywordsFr'], 'FR' )
            form.addKeywords( request.json['keywordsEn'], 'EN' )

            try:
                session.add (form)
                session.commit ()
                return jsonify({"form" : form.toJSON() })
            except Exception as e:
                print (str(e).encode(sys.stdout.encoding, errors='replace'))
                session.rollback()
                abort(make_response('Error during save', 500))

    else:
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
                for eachInput in request.json['schema']:

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
                    abort(make_response('Error', 500))


            else:
                abort(make_response('No form found with this ID', 404))

    else:
        abort(make_response('Data seems not be in ' + format +' format', 400))

# Return main page, does nothing for the moment we prefer use web services
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')