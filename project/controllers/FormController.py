# -*- coding: utf-8 -*-
# 
from project import app
from flask import Response, jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session, dbConfig
from ..models.Form import Form
from ..models.FormProperty import FormProperty
from ..models.FormFile import FormFile
from ..models.Input import Input
from ..models.InputProperty import InputProperty
from ..models.InputRepository import InputRepository
from sqlalchemy import *
import json
import sys
import datetime
from traceback import print_exc

def formsToJSON(formsQuery, short = False, jsonSchema = False):
    forms = []
    for form in formsQuery:
        if short:
            f = form.shortJSON()
        elif jsonSchema:
            f = form.toJSONSchema(session)
        else:
            f = form.recuriseToJSON(False)
        forms.append(f)
    return forms

@app.route('/forms', methods = ['GET'])
@app.route('/forms/<string:context>', methods = ['GET'])
def getForms(context = None, short = False, jsonSchema = False):
    if request.args.get('schema'):
        jsonSchema = True
    query = session.query(Form).filter_by(state = 1).order_by('name')

    # filter_by context, except for "all"
    if (context and context.lower() != "all"):
        query = query.filter_by(context = context)

    return Response(json.dumps(formsToJSON(query, short, jsonSchema), ensure_ascii=False), mimetype='application/json')

@app.route('/forms/allforms/<string:context>', methods = ['GET'])
def getFormsShort(context):
    return getForms(context, True)

@app.route('/forms/<int:pk>', methods=['GET']) # deprecated
@app.route('/form/<int:pk>', methods=['GET'])  # prefer this url, avoids ambiguity with /forms/<context>
def getForm(pk, jsonSchema = False):
    if request.args.get('schema'):
        jsonSchema = True
    form = session.query(Form).get(pk)
    if form is None:
        return abort(404)

    if jsonSchema:
        return Response(json.dumps(form.toJSONSchema(session), ensure_ascii=False), mimetype='application/json')

    jsonForm = form.recuriseToJSON(True)
    # get currently active form id
    if form.state != 1:
        currentForm = session.query(Form).filter_by(initialID = form.initialID, state = 1).first()
        if currentForm:
            jsonForm['currentForm'] = currentForm.pk_Form

    # fetch other versions
    versionsQuery = (session.query(Form)
        .filter_by(initialID = form.initialID)
        .order_by(Form.modificationDate.desc()))
    jsonForm['versions'] = formsToJSON(versionsQuery, True)

    # fetch parent forms
    jsonForm['parentForms'] = form.getParentForms(session)

    return Response(json.dumps(jsonForm, ensure_ascii=False), mimetype='application/json')

@app.route('/history/short/<int:pk>', methods = ['GET'])
def getFormShortHistory(pk):
    return getFormHistory(pk, True)

@app.route('/history/<int:pk>', methods = ['GET'])
def getFormHistory(pk, short = False):
    form = session.query(Form).get(pk)
    if form is None:
        abort(make_response('Form %d not found' % pk, 404))

    # fetch all versions except provided pk
    query = session.query(Form).filter_by(initialID = form.initialID).filter(Form.pk_Form != pk)

    return json.dumps(formsToJSON(query, short), ensure_ascii=False)

@app.route('/forms', methods = ['POST'])
@app.route('/forms/<string:context>', methods = ['POST'])
def createForm(context = None, previousID = 0):
    if not request.json:
        abort(make_response('Data seems not be in JSON format', 400))

    # check for missing properties
    for prop in Form.getColumnList():
        if not prop in request.json:
            abort(make_response('Required parameter is missing: %s' % prop, 400))

    # check for some unique name constraints
    formName = request.json['name']
    context = request.json['context']
    formTranslations = request.json['translations']
    activeForms = session.query(Form).filter(Form.pk_Form != previousID, Form.state == 1)

    # form name check
    dupeForm = activeForms.filter(Form.context == context, Form.name == formName).first()
    if dupeForm:
        abort(make_response(
            'A protocol with this name already exists -- ' +
            '{"Error":"NAME", "ID":"%d", "Context": "%s"}' % (dupeForm.pk_Form, dupeForm.context), 400))

    # form translations check
    for lang in ['fr', 'en']:
        if lang not in formTranslations:
            abort(make_response('Missing %s translations in request' % lang, 400))

        formTranslatedName = formTranslations[lang]['Name']
        dupeForm = activeForms.filter(
            Form.context == context,
            Form.FormTrad.any(Name = formTranslatedName, fk_Language = lang)).first()

        if dupeForm:
            abort(make_response(
                'A protocol with this %s name already exists -- ' % (lang.upper()) +
                '{"Error":"%sNAME", "ID":"%d", "Context":"%s"}' % (lang.upper(), dupeForm.pk_Form, dupeForm.context),
                400))

    previousForm = None
    if previousID:
        initialID = session.query(Form).filter_by(pk_Form = previousID).first().initialID
        # find previously active form with initialID
        previousForm = session.query(Form).filter_by(initialID = initialID, state = 1).first()
        if previousForm is None:
            # find previously deleted form with initialID
            previousForm = session.query(Form).filter_by(initialID = initialID, state = 3).first()
        if previousForm is None:
            abort(make_response(
                'There is no active or deleted protocol with provided initialID -- ' +
                '{"Error":"NOTFOUND", "ID":"%d", "Context":"%s"}' % (previousID, context), 404))

    formProperties = Utility._pick(request.json, Form.getColumnList())
    formExtraProperties = Utility._pickNot(request.json, Form.getColumnList() + ['fileList'])
    form = Form(**formProperties)
    form.state = 1

    initialID = previousID
    if previousForm:
        initialID = previousForm.initialID

        # restore creation date to root form's creation date
        initialForm = session.query(Form).get(initialID)
        form.creationDate = initialForm.creationDate
        form.originalID = previousForm.originalID

    form.initialID = initialID

    # add form's extra properties
    for key in formExtraProperties:
        value = formExtraProperties[key]
        if value is None:
            value = ''
        form.addProperty(FormProperty(key, value, Utility._getType(value)))

    # create form fields
    for key in request.json['schema']:
        inputDict = request.json['schema'][key]

        # set custom properties depending on field's validators
        for i in ['required', 'readonly']:
            inputDict[i] = inputDict['validators'] and inputDict['validators'].index(i) >= 0

        # delete unneeded properties
        del inputDict['validators']
        del inputDict['id']

        inputProperties = Utility._pick(inputDict, Input.getColumnsList())
        inputExtraProperties = Utility._pickNot(inputDict, Input.getColumnsList())
        input = Input(**inputProperties)

        # add input's extra properties
        for key in inputExtraProperties:
            value = inputExtraProperties[key]
            if value is None or value == []:
                value = ''
            input.addProperty(InputProperty(key, value, Utility._getType(value)))

        # add input to form
        form.addInput(input)

        # we disallow fields with same name to have different types in a context
        foundInputs = session.query(Input).filter(Input.name == input.name, Input.Form.has(state = 1)).all()
        for foundInput in foundInputs:
            # disable this check for track context
            if form.context.lower() == 'track':
                break

            # skip if previousForm (state soon to be != 1, not yet though)
            if previousForm == foundInput.Form:
                continue

            foundForm = session.query(Form).filter_by(pk_Form = foundInput.fk_form).first()
            if foundForm.context == form.context and foundInput.type != input.type:
                abort(make_response(
                    'Two fields with the same name for a given context must also share the same type -- '+
                    '{"Error":"FIELDTYPE", "ID":"%d", "FieldName":"%s", "FieldType":"%s", "Context":"%s"}' % (
                        foundForm.pk_Form, foundInput.name, foundInput.type, foundForm.context), 400))

    # check for circular dependencies with child forms
    if (form.hasCircularDependencies([], session)):
        abort(make_response('Circular dependencies appeared with child form !', 508))

    # add form files
    for fileAssoc in request.json['fileList']:
        fileAssoc['filedata'] = fileAssoc['filedata'].encode('utf-8')
        newFormFileValues = Utility._pick(fileAssoc, FormFile.getColumnList())
        formfile = FormFile(**newFormFileValues)
        form.addFile(formfile)

    try:
        session.commit()
        session.add(form)
        session.flush()
        session.commit()

        if form.initialID == 0:
            form.initialID = form.pk_Form
            session.commit()

        # set previous form's state to 2, if it was active (keep other states as is)
        if previousForm:
            if previousForm.state == 1:
                previousForm.state = 2
                session.commit()
            previousForm.updateParentForms(session, form)


    except Exception as e:
        print (str(e).encode(sys.stdout.encoding, errors='replace'))
        abort(make_response('Error during save: %s' % str(e).encode(sys.stdout.encoding, errors='replace'), 500))

    try:
        exec_exportFormBuilder(form)
    except Exception as e:
        print_exc()
        pass
    return getForm(form.pk_Form)

# PUT routes, update protocol
@app.route('/forms/<string:context>/<int:pk>', methods=['PUT'])
@app.route('/forms/<int:pk>', methods=['PUT'])
def updateForm(pk, context = None):
    # createForm actually creates a new form to keep form history
    return createForm(context, pk)

# really update form, which doesn't happen anymore
def updateForm_old(pk):
    with session.no_autoflush:
        if request.json:

            checkformname = session.query(Form).filter_by(name = request.json["name"]).first()

            if (checkformname and checkformname.pk_Form != pk):
                abort(make_response('A protocol with this name already exist ! [ERR:NAME]', 418))

            IfmissingParameters = True

            neededParametersList = Form.getColumnList()

            for a in neededParametersList : IfmissingParameters = IfmissingParameters and (a in request.json)

            if IfmissingParameters is False:
                abort(make_response('Some parameters are missing : %s' % str(neededParametersList), 400))
            else:
                form = session.query(Form).filter_by(pk_Form = pk).first()

                newFormValues   = Utility._pick(request.json, neededParametersList)
                newFormPropVals = Utility._pickNot(request.json, neededParametersList)
                del newFormPropVals['fileList']

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

                            savedConverted = None
                            if 'converted' in request.json['schema'][eachInput]:
                                savedConverted = request.json['schema'][eachInput]['converted']
                                del request.json['schema'][eachInput]['converted']

                            form.addInput( inputRepository.createInput(**inputsList) )

                            foundInputs = session.query(Input).filter_by(name = inputsList['name']).all()

                            for foundInput in foundInputs:
                                # disable this check for track context
                                if form.context.lower() != 'track':
                                    break

                                foundForm = session.query(Form).filter_by(pk_Form = foundInput.fk_form).first()
                                if foundForm.context == form.context and foundInput.type != inputsList['type']:
                                    if savedConverted == None or foundInput.pk_Input != savedConverted:#TODO REACTIVATE or len(foundInputs) > 1:
                                        abort(make_response('customerror::modal.save.inputnamehasothertype::' + str(foundInput.name) + ' = ' + str(foundInput.type), 400))
                                    
                    if len(presentInputs) > 0:
                        # We need to remove some input
                        inputRepository   = InputRepository(None)
                        inputRepository.removeInputs(presentInputs)

                    for fileAssoc in request.json['fileList']:
                        fileAssoc['filedata'] = fileAssoc['filedata'].encode('utf-8')
                        newFormFileValues   = Utility._pick(fileAssoc, FormFile.getColumnList())
                        formfile            = FormFile( **newFormFileValues )   
                        form.addFile(formfile)

                    if (form.hasCircularDependencies([], session)):
                        abort(make_response('Circular dependencies appeared with child form !', 508))

                    form.modificationDate = datetime.datetime.now()

                    neededParametersList = Form.getColumnList()

                    try:
                        session.add(form)
                    except:
                        # print (str(e).encode(sys.stdout.encoding, errors='replace'))
                        print("exception 2!")
                        print_exc()

                        session.rollback()
                        # abort(make_response('Error during save: %s' % str(e).encode(sys.stdout.encoding, errors='replace'), 500))
                    finally:
                        session.commit()
                        try: 
                            # if form.context == 'ecoreleve':
                            #     exec_exportFormBuilderEcoreleve(form.pk_Form)
                            # if form.context == 'track':
                            exec_exportFormBuilder(form)
                        except Exception as e: 
                            print("exception 3!")
                            print_exc()
                            pass
                        session.commit()
                        return jsonify(form.recuriseToJSON(True))

                else:
                    abort(make_response('No form found with this ID', 404))

        else:
            abort(make_response('Data seems to not be in ' + format + ' format', 400))


@app.route('/forms/<string:context>/<int:pk>', methods=['DELETE'])
@app.route('/forms/<int:pk>', methods=['DELETE'])
def removeForm(pk, context = None):
    form = session.query(Form).filter_by(pk_Form = pk).first()
    if form is None:
        abort(404)
    form.state = 3

    try:
        makeFormObsolete(pk)
        session.commit()
        exec_removeFormBuilderToReferential(form)
    except Exception as e:
        session.rollback()
        print_exc()
        pass
    return make_response("Successfully deleted form %d" % pk)

@app.route('/forms/<int:formid>/field/<int:inputid>', methods=['DELETE'])
def deleteInputFromForm(formid, inputid):
    return make_response("deprecated")
    form = session.query(Form).filter_by(pk_Form = formid).first()
    if form is None:
        abort(404)

    inputfield = session.query(Input).filter_by(pk_Input = inputid, fk_form = formid).first()
    if inputfield is None:
        abort(404)

    try:
        session.delete(inputfield)
        session.commit()
        return make_response("Successfully deleted field %d", inputid)
    except:
        print_exc()
        abort(make_response('Error during inputfield delete', 500))

@app.route('/forms/<string:context>/<int:formid>/deletefields', methods=['DELETE'])
@app.route('/forms/<int:formid>/deletefields', methods=['DELETE'])
def deleteInputsFromForm(formid, context):
    return make_response("deprecated")
    if not request.json or not request.json["fieldstodelete"]:
        abort(400)

    for inputID in request.json["fieldstodelete"]:
        deleteInputFromForm(formid, inputID)

    return make_response("Successfully deleted fields %s" % request.json["fieldstodelete"])

# Return main page, does nothing for the moment we prefer use web services
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')


@app.route('/childforms/<int:formid>', methods = ['GET'])
def get_childforms(formid):
    parents = session.query(Form).get(formid).getParentForms(session)
    return Response(json.dumps(parents, ensure_ascii=False), mimetype='application/json')

@app.route('/forms/getAllInputNames/<string:context>', methods = ['GET'])
def getAllInputNames(context):
    toret = []

    if (context == None or context == ""):
        context = "all"

    forms = session.query(Form).filter_by(context = context).all()
    if (context == "all"):
        forms = session.query(Form).filter_by(context != "all").all()

    for form in forms:
        for forminput in form.inputs:
            if forminput.name not in toret:
                toret.append(forminput.name)
    toret.sort()
    return Response(json.dumps(toret, ensure_ascii=False), mimetype='application/json')


@app.route('/makeObsolete/<int:formID>', methods = ['PUT'])
def makeFormObsolete(formID):
    myForm = session.query(Form).filter_by(pk_Form = formID).first()
    myForm.obsolete = True

    activeProperty = myForm.Properties.filter_by(name = 'actif').first()
    if activeProperty:
        activeProperty.value = "0"

    try:
        session.add(myForm)
        session.add(activeProperty)
        session.commit()
        exec_exportFormBuilder(myForm)
    except:
        session.rollback()
        abort(make_response('Error during delete', 500))
    finally:
        session.commit()

    return Response(json.dumps({"success":True}, ensure_ascii=False), mimetype='application/json')

# def exec_exportFormBuilderEcoreleve(formid):
#     stmt = text(""" EXEC  """+dbConfig['ecoreleve']+ """.[pr_ExportFormBuilder];
#         EXEC  """+dbConfig['ecoreleve']+ """.[pr_ImportFormBuilderOneProtocol] :formid ;
#         """).bindparams(bindparam('formid', formid))

#     curSession = session()
#     curSession.execute(stmt.execution_options(autocommit=True))

#     curSession.commit()
#     return

def exec_exportFormBuilder(form):
    context = form.context
    formid = form.pk_Form

    if not context in dbConfig:
        print("no export db configured for context %s" % context)
        return

    stmt = text("SET NOCOUNT ON; EXEC %s.[SendDataToReferential] :formToUpdate;" % dbConfig[context])
    stmt = stmt.bindparams(bindparam('formToUpdate', formid))

    curSession = session()
    try:
        curSession.execute(stmt.execution_options(autocommit=True))
        curSession.commit()
    except Exception as e:
        print("couldn't exec Remove stored procedure: %s" % e)
    return

def exec_removeFormBuilderToReferential(form):

    # myForm = session.query(Form).filter_by(pk_Form = formid).first()

    stmt = text("""SET NOCOUNT ON; EXEC """+dbConfig[form.context]+""".[RemoveFormOnReferential] :formToDelete;
        """).bindparams(bindparam('formToDelete', form.originalID))

    curSession = session()

    try:
        curSession.execute(stmt.execution_options(autocommit=True))
        curSession.commit()
    except Exception as e:
        print("couldn't exec Remove stored procedure: %s" % e)
    return