# -*- coding: utf-8 -*-
#
from project import app
from flask import jsonify, request, abort, make_response
from ..models import session
from ..models.Language import Language
import sys

# return all or one language
@app.route('/language', methods=['GET'])
@app.route('/language/<string:id>', methods=['GET'])
def getLanguage(id=None):
    """return all the available languages
    If an id is passed, return the specified language"""
    if id is not None:
        language = session.query(Language).filter_by(pk_Name=id).first()
        if language is not None:
            return jsonify(language.toJSON())
        else:
            abort(make_response('No Language for this ID', 418))
    else:
        query = session.query(Language).all()
        jsontosend = []
        for each in query:
            jsontosend.append(each.toJSON())
        if not query:
            abort(make_response('There is no Languages in database', 418))
        return jsonify(jsontosend)

# PUT routes, update language
@app.route('/language/<string:id>', methods=['PUT'])
def updateLng(id=None):
    language = session.query(Language).filter_by(pk_Name=id).first()
    try:
        if language is not None:
            lejson = request.get_json(silent=True)
            languagetoupdate = lejson['language']
            language.Label = languagetoupdate['Label']
            language.Description = languagetoupdate['Description']
            session.add(language)
            session.commit()
            return jsonify(language.toJSON())
        else:
            abort(make_response('No Language for this ID', 418))
    except Exception as exeception:
        print(str(exeception).encode(sys.stdout.encoding, errors='replace'))
        session.rollback()
        abort(make_response('Error during save: %s' % str(
            exeception).encode(sys.stdout.encoding, errors='replace'), 500))

# POST routes, create language
@app.route('/language', methods=['POST'])
def createLng():
    try:
        lejson = request.get_json(silent=True)
        print(lejson)
        languagetocreate = lejson['language']
        language = Language(
            languagetocreate['Label'], languagetocreate['Description'])
        language.pk_Name = languagetocreate['pk_Name']
        session.add(language)
        session.commit()
        return jsonify(language.toJSON())
    except Exception as exeception:
        print(str(exeception).encode(sys.stdout.encoding, errors='replace'))
        session.rollback()
        abort(make_response('Error during save: %s' % str(
            exeception).encode(sys.stdout.encoding, errors='replace'), 500))

# DELETE routes, delete language
@app.route('/language/<string:id>', methods=['DELETE'])
def deleteLng(id):
    try:
        if id is not None:
            language = session.query(Language).filter_by(pk_Name=id).first()
            if language is not None:
                session.delete(language)
                session.commit()
                return jsonify(language.toJSON())
            else:
                abort(make_response('No Language for this ID', 418))
        else:
            abort(make_response('Argument ID missing', 500))
    except Exception as exeception:
        print(str(exeception).encode(sys.stdout.encoding, errors='replace'))
        session.rollback()
        abort(make_response('Error during save: %s' % str(
            exeception).encode(sys.stdout.encoding, errors='replace'), 500))
