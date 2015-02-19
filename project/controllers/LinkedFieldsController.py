# -*- coding: utf-8 -*-
from project                    import app
from flask                      import jsonify, request, make_response
from ..models                   import session
from ..utilities                import Utility

import ConfigParser
import urllib2
import os
import sys
import datetime
import json

@app.route('/linked', methods = ['GET'])
def getLinkedFields():
    Config = ConfigParser.ConfigParser()
    Config.read("project/config/config.ini")

    linkedFieldsList = []
    # Get all webServices link
    for each in Config.options("webServices"):
        try:
            url     = Config.get("webServices", each)
            content = urllib2.urlopen(url, timeout = 1).read()

            # For each request we add the linked fields at the list
            linkedFieldsList = linkedFieldsList + json.loads(content)
        except urllib2.URLError, e:
            pass

    return jsonify({"linkedFields" : linkedFieldsList})