# -*- coding: utf-8 -*-
# 
from project import app
from flask import jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session, engine,dbConfig
from ..models.Form import Form
from ..models.FormProperty import FormProperty
from ..models.FormFile import FormFile
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
from traceback import print_exc
import transaction

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

@app.route('/forms/<string:context>/<formID>', methods = ['GET'])
def getFormByIDWithContext(context, formID):
    return(getFormByID(formID))

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


@app.route('/forms/<string:context>', methods = ['POST'])
def createFormWithContext(context):
    return(createForm())

# Create form
@app.route('/forms', methods = ['POST'])
def createForm():

    if request.json:

        checkformname = session.query(Form).filter_by(name = request.json["name"]).first()
        checkformnamefr = session.query(Form).filter_by(labelFr = request.json["labelFr"]).first()
        checkformnameen = session.query(Form).filter_by(labelEn = request.json["labelEn"]).first()

        if (checkformname and checkformname.pk_Form != id):
            abort(make_response('A protocol with this name already exist ! [ERR:NAME]', 418))
        if (checkformnamefr and checkformnamefr.pk_Form != id):
            abort(make_response('A protocol with this french name already exist ! [ERR:FRNAME]', 418))
        if (checkformnameen and checkformnameen.pk_Form != id):
            abort(make_response('A protocol with this english name already exist ! [ERR:ENNAME]', 418))

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

            del newFormPropVals['fileList']

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
            
            for fieldset in request.json['fieldsets']:
                # TODO FIX
                newfieldset = Fieldset(fieldset['legend'], ",".join(fieldset['fields']), False, fieldset['legend'] + " " + fieldset['cid'], fieldset['order'])#fieldset['LOL']
                form.addFieldset(newfieldset)

            if (form.hasCircularDependencies([], session)):
                abort(make_response('Circular dependencies appeared with child form !', 508))

            for fileAssoc in request.json['fileList']:
                fileAssoc['filedata'] = fileAssoc['filedata'].encode('utf-8')
                newFormFileValues   = Utility._pick(fileAssoc, FormFile.getColumnList())
                formfile            = FormFile( **newFormFileValues )   
                form.addFile(formfile)

            try:
                for each in form.keywords :
                    session.delete(each.KeyWord)
                    session.delete(each)
                session.commit()

                form.setKeywords( request.json['keywordsFr'], 'FR' )
                form.setKeywords( request.json['keywordsEn'], 'EN' )
                session.add(form)
                session.flush()
            except Exception as e:
                print (str(e).encode(sys.stdout.encoding, errors='replace'))
                session.rollback()
                abort(make_response('Error during save: %s' % str(e).encode(sys.stdout.encoding, errors='replace'), 500))

            finally:
                session.commit()
                try: 
                    # if form.context == 'ecoreleve':
                    #     exec_exportFormBuilderEcoreleve(form.pk_Form)
                    # if form.context == 'track':
                    exec_exportFormBuilder(form)
                except Exception as e: 
                    print("exception 1!")
                    print_exc()
                    pass
                session.commit()
                return jsonify({"form" : form.recuriseToJSON() })
    else:
        abort(make_response('Data seems not be in JSON format', 400))

@app.route('/forms/<string:context>/<int:id>', methods=['PUT'])
def updateFormWithContext(context, id):
    return (updateForm(id))

# PUT routes, update protocol
@app.route('/forms/<int:id>', methods=['PUT'])
def updateForm(id):
    with session.no_autoflush:
        if request.json:

            checkformname = session.query(Form).filter_by(name = request.json["name"]).first()
            checkformnamefr = session.query(Form).filter_by(labelFr = request.json["labelFr"]).first()
            checkformnameen = session.query(Form).filter_by(labelEn = request.json["labelEn"]).first()

            if (checkformname and checkformname.pk_Form != id):
                abort(make_response('A protocol with this name already exist ! [ERR:NAME]', 418))
            if (checkformnamefr and checkformnamefr.pk_Form != id):
                abort(make_response('A protocol with this french name already exist ! [ERR:FRNAME]', 418))
            if (checkformnameen and checkformnameen.pk_Form != id):
                abort(make_response('A protocol with this english name already exist ! [ERR:ENNAME]', 418))

            IfmissingParameters = True

            neededParametersList = Form.getColumnList()

            for a in neededParametersList : IfmissingParameters = IfmissingParameters and (a in request.json)

            if IfmissingParameters is False:
                abort(make_response('Some parameters are missing : %s' % str(neededParametersList), 400))
            else:
                form = session.query(Form).filter_by(pk_Form = id).first()

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
                                foundForm = session.query(Form).filter_by(pk_Form = foundInput.fk_form).first()
                                if foundForm.context == form.context and foundInput.type != inputsList['type']:
                                    if savedConverted == None or foundInput.pk_Input != savedConverted:#TODO REACTIVATE or len(foundInputs) > 1:
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

                        for each in form.keywords :
                            session.delete(each.KeyWord)
                            session.delete(each)
                        session.commit()

                        form.setKeywords( request.json['keywordsFr'], 'FR' )
                        form.setKeywords( request.json['keywordsEn'], 'EN' )

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
                        return jsonify({"form" : form.recuriseToJSON() })

                else:
                    abort(make_response('No form found with this ID', 404))

        else:
            abort(make_response('Data seems to not be in ' + format + ' format', 400))

@app.route('/forms/<string:context>/<int:id>', methods=['DELETE'])
def removeFormWithContext(context, id):
    return (removeForm(id))

@app.route('/forms/<int:id>', methods=['DELETE'])
def removeForm(id):
    form = session.query(Form).filter_by(pk_Form = id).first()

    try:
        session.delete(form)
    except:
        session.rollback()
        abort(make_response('Error during delete', 500))
    finally:
        session.commit()
        try: 
            # if form.context == 'track':
            exec_removeFormBuilderToReferential(form)

        except Exception as e: 
            print_exc()
            pass
        session.commit()
    return jsonify({"deleted" : True})

@app.route('/forms/<int:formid>/field/<int:inputid>', methods=['DELETE'])
def deleteInputFromForm(formid, inputid):
    form = session.query(Form).filter_by(pk_Form = formid).first()
    inputfield = session.query(Input).filter_by(pk_Input = inputid, fk_form = formid).first()

    if (inputfield != None):
        try:
            session.delete(inputfield)
            session.commit()
            return jsonify({"deleted" : True})
        except:
            session.rollback()
            abort(make_response('Error during inputfield delete', 500))

@app.route('/forms/<string:context>/<int:formid>/deletefields', methods=['DELETE'])
def deleteInputsFromFormWithContext(context, formid):
    return deleteInputsFromForm(formid)

@app.route('/forms/<int:formid>/deletefields', methods=['DELETE'])
def deleteInputsFromForm(formid):
    if request.json:
        if request.json["fieldstodelete"]:
            for inputID in request.json["fieldstodelete"]:
                deleteInputFromForm(formid, inputID)

        return jsonify({"deleted" : True})

# Return main page, does nothing for the moment we prefer use web services
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')


@app.route('/forms/allforms', methods = ['GET'])
def quick_getAllForms():
    return self.fetAllFormsInContext("")


@app.route('/forms/allforms/<string:context>', methods = ['GET'])
def getAllFormsInContext(context):
    if (context == None):
        context = ""
    forms = []

    forms_added        = []
    keywords_added     = []
    current_form_index = -1

    query   = session.query(Form).order_by(Form.name)
    results = query.all()

    for form in results:
        if (context == "" or form.context == context):
            f = {"id":form.pk_Form,"name":form.name, "context":form.context, "obsolete":form.obsolete}
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
    return json.dumps(toret, ensure_ascii=False)


@app.route('/makeObsolete/<int:formID>', methods = ['PUT'])
def makeFormObsolete(formID):
    
    myForm = session.query(Form).filter_by(pk_Form = formID).first()
    myForm.obsolete = True

    try:
        session.add(myForm)
    except:
        session.rollback()
        abort(make_response('Error during delete', 500))
    finally:
        session.commit()

    return json.dumps({"success":True}, ensure_ascii=False)

def exec_exportFormBuilderEcoreleve(formid):
    stmt = text(""" EXEC  """+dbConfig['ecoreleve']+ """.[pr_ExportFormBuilder];
        EXEC  """+dbConfig['ecoreleve']+ """.[pr_ImportFormBuilderOneProtocol] :formid ;
        """).bindparams(bindparam('formid', formid))

    curSession = session()
    curSession.execute(stmt.execution_options(autocommit=True))

    curSession.commit()
    return

def exec_exportFormBuilder(form):
    context = form.context
    formid = form.pk_Form

    stmt = text("""SET NOCOUNT ON; EXEC """+dbConfig[context]+""".[SendDataToReferential] :formToUpdate;
        """).bindparams(bindparam('formToUpdate', formid))

    curSession = session()
    curSession.execute(stmt.execution_options(autocommit=True))

    curSession.commit()

    return

def exec_removeFormBuilderToReferential(form):

    # myForm = session.query(Form).filter_by(pk_Form = formid).first()

    stmt = text("""SET NOCOUNT ON; EXEC """+dbConfig[form.context]+""".[RemoveFormOnReferential] :formToDelete;
        """).bindparams(bindparam('formToDelete', form.originalID))

    curSession = session()
    curSession.execute(stmt.execution_options(autocommit=True))

    curSession.commit()
    return