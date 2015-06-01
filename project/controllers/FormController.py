# -*- coding: utf-8 -*-
# 
from project import app
from flask import jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session
from ..models.Form import Form
from ..models.Input import Input
from ..models.InputProperty import InputProperty
from ..models.InputRepository import InputRepository
from ..models.Fieldset import Fieldset
import json
import sys

# Return all forms
@app.route('/forms', methods = ['GET'])
def getForms():

    # Forms list who will be returned at the end
    forms = []
    # Used to stock each form yet added
    formsAdded = []
    # Current form iteration
    currentFormIndex = -1

    query   = session.query(Form, Input, InputProperty).join(Input).join(InputProperty)
    results = query.all()

    for each in results:
        if each[0].pk_Form not in formsAdded:
            # Add form to the list and update current index
            forms.append(each[0].toJSON())
            currentFormIndex += 1
            # Initialize schema attribute
            forms[currentFormIndex]["schema"] = {}
            # Mark this current as added
            formsAdded.append(each[0].pk_Form)

        # Add field if it is not yet done
        if each[1].name not in forms[currentFormIndex]["schema"] and each[1].curStatus != 4:
            forms[currentFormIndex]["schema"][each[1].name] = each[1].toJSON()

        if each[1].curStatus != 4:
            forms[currentFormIndex]["schema"][each[1].name][each[2].name] = each[2].getvalue()

    return json.dumps(forms, ensure_ascii=False)

# Get protocol by ID
@app.route('/forms/<formID>', methods = ['GET'])
def getFormByID(formID):
    findForm = session.query(Form).filter_by(pk_Form = formID)
    if findForm.count() > 0:
        return jsonify({ "form" : findForm.one().toJSON() })
    else:
        abort (404, 'No form found')

# Create form
@app.route('/forms', methods = ['POST'])
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

                try:
                    inputsList['required'] = inputsList['validators'].index('required') >= 0
                except ValueError:
                    inputsList['required'] = False

                try:
                    inputsList['readonly'] = inputsList['validators'].index('readonly') >= 0
                except ValueError:
                    inputsList['readonly'] = False

                del inputsList['validators']
                del inputsList['id']

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

            for fieldset in request.json['fieldsets']:
                newfieldset = Fieldset(fieldset['legend'], ",".join(fieldset['fields']), False)
                form.addFieldset(newfieldset)

            try:
                session.add (form)
                session.commit ()
                return jsonify({"form" : form.recuriseToJSON() })
            except Exception as e:
                print (str(e).encode(sys.stdout.encoding, errors='replace'))
                session.rollback()
                abort(make_response('Error during save', 500))

    else:
        abort(make_response('Data seems not be in JSON format', 400))

# PUT routes, update protocol
@app.route('/forms/<int:id>', methods=['PUT'])
def updateForm(id):
    if request.json:

        IfmissingParameters = True

        neededParametersList = Form.getColumnList()

        for a in neededParametersList : IfmissingParameters = IfmissingParameters and (a in request.json)

        if IfmissingParameters is False:
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

                    if request.json['schema'][eachInput]['id'] in presentInputs:

                        # the field is present we update it
                        foundInput        = session.query(Input).filter_by(pk_Input = request.json['schema'][eachInput]['id']).first()
                        inputRepository   = InputRepository(foundInput)

                        inputNewValues    = request.json['schema'][eachInput]

                        # foundInputUpdated = inputRepository.updateInput(**inputNewValues)
                        inputRepository.updateInput(**inputNewValues)

                        presentInputs.remove(foundInput.pk_Input)

                    else:
                        inputRepository   = InputRepository(None)
                        # Add a new input to the form

                        inputsList = request.json['schema'][eachInput]

                        try:
                            inputsList['required'] = inputsList['validators'].index('required') >= 0
                        except ValueError:
                            inputsList['required'] = False

                        try:
                            inputsList['readonly'] = inputsList['validators'].index('readonly') >= 0
                        except ValueError:
                            inputsList['readonly'] = False

                        form.addInput( inputRepository.createInput(**inputsList) )


                if len(presentInputs) > 0:
                    # We need to remove some input
                    inputRepository   = InputRepository(None)
                    inputRepository.removeInputs(presentInputs)

                # form.addKeywords( request.json['keywords'] )

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

@app.route('/forms/<int:id>', methods=['DELETE'])
def removeForm(id):
    form = session.query(Form).filter_by(pk_Form = id).first()

    try:
        session.delete(form)
        session.commit()
        return jsonify({"deleted" : True})
    except:
        session.rollback()
        abort(make_response('Error during delete', 500))

# Return main page, does nothing for the moment we prefer use web services
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')