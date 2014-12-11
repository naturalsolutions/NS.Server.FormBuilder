# -*- coding: utf-8 -*-
from project                import app
from flask                  import jsonify, abort, render_template, request, make_response
from ..models               import session, Form, KeyWord, Unity

import os
import sys
import datetime

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
@app.route('/protocols', methods = ['GET'])
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
@app.route('/protocols/<formName>', methods = ['GET'])
def getProtocolsByName(formName):
    forms = session.query(Form).filter_by(Name = formName)
    if forms.count() > 0:
        return jsonify({ formName : forms.one().toJSON() })
    else:
        abort (404, 'Form found for this name')


#   -------------------------------------------------------
# POST routes, create a form with name and content
@app.route('/protocols', methods = ['POST'])
def createProtocole():

    if request.json:

        #   Check if all parameters are present
        IfmissingParameters = True

        neededParametersList = [
            'name',
            'description',
            'keywords',
            'labelFr',
            'labelEn',
            'schema',
            'fieldsets'
        ]

        for a in neededParametersList : IfmissingParameters = IfmissingParameters and (a in request.json)

        if IfmissingParameters == False:

            abort(make_response('Some parameters are missing', 400))

        else:

            #   Check if a form with this name exists
            forms = session.query(Form).filter_by(Name = request.json['name'])

            if forms.count() == 0:
                # No, we create a new form
                form = Form(request.json['name'], request.json['labelFr'], request.json['labelEn'], request.json['description'])
            else:

                #   Yes, we get the first form and we update it 
                #   Maybe we can send an error here and only allow form update on PUT method ?
                form = forms.first()

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
                abort(make_response('Error during save', 500))

    else:
        abort(make_response('Data seems not be in ' + format +' format', 400))


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
    configuration    = Session.query(Configuration).all()
    configurations   = []
    for each in configuration :
        configurations.append( each.type )
    return jsonify({ "options" : configurations})


@app.route('/configurations', methods = ['POST'])
def createConfiguratedField():
    if not request.json:
        self.wrongFormat('JSON')
    elif not 'field' in request.json:
        self.missingParameters()
    else:
        if all (k in request.json['field'] for k in ("type","name", "content")):
            # All parameter are present
            newConfiguratedField = Configuration(request.json['field']['type'], request.json['field']['name'], "")

            try:
                Session.add (newConfiguratedField)
                Session.commit ()
                return jsonify({ "result" : True})
            except:
                Session.rollback()
                print "Unexpected error:", sys.exc_info()[0]
                return jsonify({ "result" : False})
        else:
            self.missingParameters();


@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')




