# -*- coding: utf-8 -*-
from project import app
from ..models import session
from ..models.KeyWord import KeyWord
from flask import jsonify

# return all keywords
@app.route('/keywords', methods = ['GET'])
def getKeywords():
    keywords = session.query(KeyWord).all()
    ks   = []
    for each in keywords:
        ks.append( each.toJSON() )
    return jsonify ({ "options" : ks })