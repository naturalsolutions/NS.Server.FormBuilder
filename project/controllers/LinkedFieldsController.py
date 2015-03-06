# -*- coding: utf-8 -*-
from project                    import app
from flask                      import jsonify, request, make_response
from ..models                   import session
from ..utilities                import Utility

import urllib.request
import json

@app.route('/linked', methods = ['GET'])
def getLinkedFields():
    with open ("project/config/config.json", "r") as myfile:
        data = json.loads( myfile.read() )        

    linkedFieldsList = []
    # Get all webServices link
    for each in data["webServices"]:
        try:
            url     = data["webServices"][each]
            content = urlopen(url, timeout = 1).read()

            # For each request we add the linked fields at the list
            linkedFieldsList = linkedFieldsList + json.loads(content)
        except:
            pass

    return jsonify({"linkedFields" : linkedFieldsList})