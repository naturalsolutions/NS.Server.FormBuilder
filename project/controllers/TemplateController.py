# -*- coding: utf-8 -*-
#
from project import app
from flask import jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session
from ..models.Form import Form
from ..models.InputProperty import InputProperty
from ..models.Input import Input
from ..models.InputProperty import InputProperty
from ..models.InputRepository import InputRepository
from ..models.Fieldset import Fieldset
import json
import sys
import datetime

import pprint

# Return all forms
@app.route('/templates', methods = ['GET'])
def templates():

    # Forms list who will be returned at the end
    forms = []
    # Used to stock each form yet added
    formsAdded = []
    # Current form iteration
    currentFormIndex = -1

    query   = session.query(Form, Input, InputProperty).join(Input).join(InputProperty).order_by(Form.name).filter(Form.isTemplate == True)
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

@app.route('/templates/<int:id>', methods = ['GET'])
def templateById(id):

    # Forms list who will be returned at the end
    forms = []
    # Used to stock each form yet added
    formsAdded = []
    # Current form iteration
    currentFormIndex = -1

    query   = session.query(Form, Input, InputProperty).join(Input).join(InputProperty).filter(Form.pk_Form == id).filter(Form.isTemplate == True)
    results = query.all()

    print (len(results))

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

# Create form
@app.route('/templates', methods = ['POST'])
def create_template():

    if request.json:
        #   Check if all parameters are present
        IfmissingParameters = True

        neededParametersList = Form.getColumnList()

        pprint.pprint(neededParametersList)
        pprint.pprint(request.json)

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