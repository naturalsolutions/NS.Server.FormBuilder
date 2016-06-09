# -*- coding: utf-8 -*-
# 
from project import app
from flask import jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session, engine
from ..models.Form import Form
from ..models.FormProperty import FormProperty
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
    print(session())
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
    if (formID.isdigit()):
        findForm = session.query(Form).get(formID)
        return jsonify({ "form" : findForm.recuriseToJSON() })
    else:
        forms = []

        forms_added        = []
        keywords_added     = []
        current_form_index = -1

        query   = session.query(Form, KeyWord_Form).outerjoin(KeyWord_Form).order_by(Form.name)
        results = query.all()

        for form, keyword in results:
            if form.pk_Form not in forms_added and (form.context == formID or formID.lower() == "all"):
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

# Create form
@app.route('/forms', methods = ['POST'])
def createForm():

    if request.json:
        #   Check if all parameters are present
        IfmissingParameters = True
        neededParametersList = Form.getColumnList()
        for a in neededParametersList:
            IfmissingParameters = IfmissingParameters and (a in request.json)

        if IfmissingParameters == False:
            abort(make_response('Some parameters are missing : %s' % str(neededParametersList), 400))
        else:
            newFormValues   = Utility._pick(request.json, neededParametersList)
            newFormPropVals = Utility._pickNot(request.json, neededParametersList)
            form            = Form( **newFormValues )              # new form Object

            for prop in newFormPropVals:
                if newFormPropVals[prop] == None :
                    newFormPropVals[prop] = ''
                formProperty = FormProperty(prop, newFormPropVals[prop], Utility._getType(newFormPropVals[prop]))
                form.addProperty(formProperty)

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

                # abort(make_response('inputsList : %s \nand %s \nand %s \nand %s' % (str(inputsList), str(inputColumnList), str(form), str(request.json)), 400))

                newInputValues          = Utility._pick(inputsList, inputColumnList)        # new input values
                newPropertiesValues     = Utility._pickNot(inputsList, inputColumnList)     # properties values
                newInput                = Input( **newInputValues )                         # new Input object

                # Add properties to the new configurated field
                for prop in newPropertiesValues:
                    # TODO FIND BETTER WORKAROUND
                    if newPropertiesValues[prop] == None or newPropertiesValues[prop] == []:
                        newPropertiesValues[prop] = ''
                    property = InputProperty(prop, newPropertiesValues[prop], Utility._getType(newPropertiesValues[prop]))
                    newInput.addProperty(property)

                # Add new input to the form
                form.addInput(newInput)
                foundInputs = session.query(Input).filter_by(name = newInput.name).all()

                for foundInput in foundInputs:
                    foundForm = session.query(Form).filter_by(pk_Form = foundInput.fk_form).first()
                    if foundForm.context == form.context and foundInput.type != newInput.type:
                        abort(make_response('customerror::modal.save.inputnamehasothertype::' + str(foundInput.name) + ' = ' + str(foundInput.type), 400))
            
            form.addKeywords( request.json['keywordsFr'], 'FR' )
            form.addKeywords( request.json['keywordsEn'], 'EN' )

            for fieldset in request.json['fieldsets']:
                # TODO FIX
                newfieldset = Fieldset(fieldset['legend'], ",".join(fieldset['fields']), False, fieldset['legend'] + " " + fieldset['cid'], fieldset['order'])#fieldset['LOL']
                form.addFieldset(newfieldset)

            try:
                session.add (form)
                session.commit ()
                return jsonify({"form" : form.recuriseToJSON() })
            except Exception as e:
                print (str(e).encode(sys.stdout.encoding, errors='replace'))
                session.rollback()
                abort(make_response('Error during save: %s' % str(e).encode(sys.stdout.encoding, errors='replace'), 500))

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
            abort(make_response('Some parameters are missing : %s' % str(neededParametersList), 400))
        else:
            form = session.query(Form).filter_by(pk_Form = id).first()

            newFormValues   = Utility._pick(request.json, neededParametersList)
            newFormPropVals = Utility._pickNot(request.json, neededParametersList)
            form.update(**newFormValues)              # new form Object
            form.updateProperties(newFormPropVals)

            if form != None:

                # Get form input ID list
                presentInputs = form.getInputsIdList()

                # We check if input in JSON data are yet present in the form
                # Yes : we update input
                # No : we add an input to the form
                for eachInput in request.json['schema']:
                    inputsList = request.json['schema'][eachInput]

                    try:
                        request.json['schema'][eachInput]['required'] = request.json['schema'][eachInput]['validators'].index('required') >= 0
                    except:
                        request.json['schema'][eachInput]['required'] = False
                        pass

                    try:
                        request.json['schema'][eachInput]['readonly'] = request.json['schema'][eachInput]['validators'].index('readonly') >= 0
                    except:
                        request.json['schema'][eachInput]['readonly'] = False
                        pass

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
                        del request.json['schema'][eachInput]['id']
                        inputRepository   = InputRepository(None)
                        # Add a new input to the form

                        inputsList = request.json['schema'][eachInput]

                        form.addInput( inputRepository.createInput(**inputsList) )

                        foundInputs = session.query(Input).filter_by(name = inputsList['name']).all()

                        for foundInput in foundInputs:
                            foundForm = session.query(Form).filter_by(pk_Form = foundInput.fk_form).first()
                            if foundForm.context == form.context and foundInput.type != inputsList['type']:
                                abort(make_response('customerror::modal.save.inputnamehasothertype::' + str(foundInput.name) + ' = ' + str(foundInput.type), 400))
                    

                if len(presentInputs) > 0:
                    # We need to remove some input
                    inputRepository   = InputRepository(None)
                    inputRepository.removeInputs(presentInputs)

                for each in form.fieldsets:
                    each.curStatus = 4

                for each in request.json['fieldsets']:
                    # TODO FIX
                    form.addFieldset(Fieldset(each['legend'], ",".join(each['fields']), False, each['legend'] + " " + each['cid'], each['order']))

                form.addKeywords( request.json['keywordsFr'], 'FR' )
                form.addKeywords( request.json['keywordsEn'], 'EN' )

                form.modificationDate = datetime.datetime.now()

                neededParametersList = Form.getColumnList()

                try:
                    session.add (form)
                    session.commit ()
                    return jsonify({"form" : form.recuriseToJSON() })
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

@app.route('/forms/<string:context>/<int:id>', methods=['DELETE'])
def removeFormInContext(context, id):
    form = session.query(Form).filter_by(pk_Form = id).first()

    try:
        session.delete(form)
        session.commit()
        return jsonify({"deleted" : True})
    except:
        session.rollback()
        abort(make_response('Error during delete', 500))

@app.route('/forms/<int:formid>/field/<int:inputid>', methods=['DELETE'])
def deleteInputFromForm(formid, inputid):
    form = session.query(Form).filter_by(pk_Form = formid).first()
    inputfield = session.query(Input).filter_by(pk_Input = inputid, fk_form = formid).first()

    try:
        session.delete(inputfield)
        session.commit()
        return jsonify({"deleted" : True})
    except:
        session.rollback()
        abort(make_response('Error during inputfield delete', 500))

# Return main page, does nothing for the moment we prefer use web services
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')


@app.route('/forms/allforms', methods = ['GET'])
def quick_getAllForms():
    forms = []

    forms_added        = []
    keywords_added     = []
    current_form_index = -1

    query   = session.query(Form).order_by(Form.name)
    results = query.all()

    for form in results:
        f = {"id":form.pk_Form,"name":form.name, "context":form.context}
        current_form_index += 1
        forms.append(f)
        forms_added.append(form.pk_Form)

    return json.dumps(forms, ensure_ascii=False)



@app.route('/childforms/<int:formid>', methods = ['GET'])
def get_childforms(formid):
    forms = []

    forms_added        = []
    keywords_added     = []
    current_form_index = -1

    if (formid > 0):
        formName = session.query(Form).filter_by(pk_Form = formid).first().name

        for childFormInputProp in session.query(InputProperty).filter_by(value = formName, name = "childFormName").all():
            childFormInput = session.query(Input).filter_by(pk_Input = childFormInputProp.fk_Input).first()
            childForm = session.query(Form).filter_by(pk_Form = childFormInput.fk_form).first()
            if childForm.pk_Form not in forms_added:
                f = {"id":childForm.pk_Form,"name":childForm.name}
                current_form_index += 1
                forms.append(f)
                forms_added.append(childForm.pk_Form)

    return json.dumps(forms, ensure_ascii=False)