# -*- coding: utf-8 -*-
from project                    import app
from flask                      import jsonify
from ..models                   import session, Unity

#   Return all unit values
@app.route('/unities', methods = ['GET'])
def getUnities():
    unities = session.query(Unity).all()
    un   = []
    for each in unities:
        un.append( each.toJSON() )
    return jsonify ({ "options" : un })