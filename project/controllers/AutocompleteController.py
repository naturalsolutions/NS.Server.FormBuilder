# -*- coding: utf-8 -*-
# 
from project import app
from ..models import session
from ..models.Form import Form
from flask import jsonify, abort, render_template, request, make_response
from sqlalchemy import *
from ..controllers import TrackController
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
	context = request.json["context"]
	if (context == "track"):
		trackEngine = TrackController.getTrackSqlConnection()
		if (trackEngine != None):
			toret = []
			result = trackEngine.execute(request.json["sqlQuery"])
			for row in result:
				toret.append(row[0])
			return json.dumps(toret, ensure_ascii=False)
	else:
		abort(make_response('Not implemented yet !', 400))