# -*- coding: utf-8 -*-
# 
from project import app
from ..models import session
from ..models.Form import Form
from flask import jsonify, abort, render_template, request, make_response
from sqlalchemy import *
import urllib.parse
import json
import sys
import datetime
import pprint

# Return all forms
@app.route('/autocomplete/forms', methods = ['GET'])
def getFormName():
    query = session.query(Form.name).all()

    forms = []
    for eachInput in query:
        forms.append(eachInput[0])

    return json.dumps({"options":forms})

# Returns values for autocomplete from SQL Query
@app.route('/sqlAutocomplete', methods = ['POST'])
def getValuesFromRequest():
	abort(make_response('Not implemented yet !', 400))