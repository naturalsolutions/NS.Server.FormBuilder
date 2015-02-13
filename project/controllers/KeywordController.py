# -*- coding: utf-8 -*-
from project                    import app
from flask                      import jsonify
from ..models                   import session, KeyWord

# return all keywords
@app.route('/keywords', methods = ['GET'])
def getKeywords():
    keywords = session.query(KeyWord).all()
    ks   = []
    for each in keywords:
        ks.append( each.toJSON() )
    return jsonify ({ "options" : ks })