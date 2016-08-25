# -*- coding: utf-8 -*-
from project import app
from flask import jsonify
from ..models import session
from ..models.Unity import Unity

#   Return all unit values
@app.route('/unities', methods = ['GET'])
def getUnities():
    unities = session.query(Unity).all()
    un   = []
    for each in unities:
        un.append( each.toJSON() )
    return jsonify ({ "options" : un })

#   Return all unit values
@app.route('/unities/<string:context>', methods = ['GET'])
def getUnitiesWithContext(context):
    unities = session.query(Unity).all()
    un   = []
    for each in unities:
    	if each.context == context:
        	un.append(each.toJSON())
    return jsonify ({ "unities" : un })