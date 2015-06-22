# -*- coding: utf-8 -*-
# 
from project import app
from flask import jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session, engine
from ..models.Form import Form
from ..models.KeyWord_Form import KeyWord_Form
from ..models.Input import Input
from ..models.InputProperty import InputProperty
from ..models.InputRepository import InputRepository
from ..models.Fieldset import Fieldset
from sqlalchemy import *
import json
import sys
import datetime
import pprint

# Return all forms
@app.route('/forms', methods = ['GET'])
def get_forms():

    # Forms list who will be returned at the end
    forms = []

    forms_added        = []
    keywords_added     = []
    current_form_index = -1

    query   = session.query(Form, KeyWord_Form).outerjoin(KeyWord_Form).order_by(Form.name)
    results = query.all()

    for form, keyword in results:

        if form.pk_Form not in forms_added:
            f = form.to_json()
            current_form_index += 1
            f['keywordsFr'] = []
            f['keywordsEn'] = []
            forms.append(f)
            forms_added.append(form.pk_Form)

        if keyword is not None and keyword.curStatus != 4 and keyword.pk_KeyWord_Form not in keywords_added:
            k = keyword.toJSON()
            forms[current_form_index]['keywordsFr' if k['lng'] == 'FR' else 'keywordsEn'].append(k)
            keywords_added.append(keyword.pk_KeyWord_Form)

    return json.dumps(forms, ensure_ascii=False)

# Get protocol by ID
@app.route('/forms/<formID>', methods = ['GET'])
def getFormByID(formID):
    findForm = session.query(Form).filter_by(pk_Form = formID)
    if findForm.count() > 0:
        return jsonify({ "form" : findForm.one().recuriseToJSON() })
    else:
        abort (404, 'No form found')

# Create form
@app.route('/forms', methods = ['POST'])
def createForm():

    if request.json:
        #   Check if all parameters are present
        IfmissingParameters = True

        neededParametersList = Form.getColumnList()

        for a in neededParametersList: IfmissingParameters = IfmissingParameters and (a in request.json)

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
                except:
                    inputsList['required'] = False

                try:
                    inputsList['readonly'] = inputsList['validators'].index('readonly') >= 0
                except:
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

                    try:
                        request.json['schema'][eachInput]['required'] = request.json['schema'][eachInput]['validators'].index('required') >= 0
                    except:
                        request.json['schema'][eachInput]['required'] = False

                    try:
                        request.json['schema'][eachInput]['readonly'] = request.json['schema'][eachInput]['validators'].index('readonly') >= 0
                    except:
                        request.json['schema'][eachInput]['readonly'] = False

                    del request.json['schema'][eachInput]['validators']

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

                for each in form.fieldsets:
                    each.curStatus = 4

                for each in request.json['fieldsets']:
                    form.addFieldset(Fieldset(each['legend'], ",".join(each['fields']), False))

                form.addKeywords( request.json['keywordsFr'], 'FR' )
                form.addKeywords( request.json['keywordsEn'], 'EN' )

                form.modificationDate = datetime.datetime.now()

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
        abort(make_response('Data seems not be in ' + format + ' format', 400))

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