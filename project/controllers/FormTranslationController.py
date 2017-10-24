# -*- coding: utf-8 -*-
#
from project import app
from flask import jsonify, request, abort, make_response
from sqlalchemy import func
from ..models import session
from ..models.FormTrad import FormTrad
import sys

#Test an array of string if exists in FormTrad
@app.route('/formtranslation/exists', methods=['POST'])
def ifexists():
    """accept json array {"names":[]} with the translated names 
    return a boolean : true if already exists, false if not"""
    requestjson = request.get_json(silent=True)
    names = requestjson['names']
    query = session.query(FormTrad).filter(func.lower(FormTrad.Name).in_([x.lower() for x in names])).first()
    if query :
        return jsonify({"exists":"True", "existingLanguage":query.fk_Language})
    else:
        return jsonify({"exists":"False"})

# PUT routes, update translations
@app.route('/formtranslation/<int:formid>', methods=['PUT'])
def updateAll(formid):
    """update a list of translation
    For an existing Form it will update delete and add languages
    You'll need to send all the tranqlations at once in order to proceed"""
    json = request.get_json(silent=True)
    transtoupdate = json['translations']
    query = session.query(FormTrad).filter_by(fk_Form = formid).all()
    #print(transtoupdate)
    if not query:
        abort(make_response('This Form does not exist', 418))
    try:
        for each in query:
            test = [t for t in transtoupdate if t['fk_Language'] == each.fk_Language]
            if not test:
                session.delete(each)
            else:
                each.Name = test[0]['Name']
                each.Description = test[0]['Description']    
                transtoupdate.remove(test[0])            
                session.add(each)
        if transtoupdate:
            for each in transtoupdate:
                newtrans = FormTrad(each['Name'], each['Description'])
                newtrans.fk_Form = formid
                newtrans.fk_Language = each['fk_Language']
                session.add(newtrans)
                
    except Exception as exeception:
        print (str(exeception).encode(sys.stdout.encoding, errors='replace'))
        session.rollback()
        abort(make_response('Error during save: %s' % str(exeception).encode(sys.stdout.encoding, errors='replace'), 500))
    session.commit()
