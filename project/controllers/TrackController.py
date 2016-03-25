# -*- coding: utf-8 -*-
#
from project import app
from flask import jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session, engine
from sqlalchemy import *
import json
import sys
import datetime
import pprint

@app.route('/Track/getData', methods = ['POST'])
def getData():
	if 'datas' in request.json:
		toret = {}
		with open ("project/config/config.json", "r") as myfile:
			data = json.loads(myfile.read())
		trackSqlConnexion = data["sql"]["urlTrack"] if 'sql' in data and 'urlTrack' in data['sql'] else abort(make_response('config.json file has no url referencing Track Database !', 400))

		try:
			trackEngine = create_engine(trackSqlConnexion)
		except e as Exception:
			abort(make_response('Could not open database !', 400))
		else:

			for dataType in request.json["datas"]:
				toret[dataType] = {}
				result = trackEngine.execute("SELECT DISTINCT [TPro_"+dataType+"] FROM [TProtocole]")
				for row in result:
					toret[dataType][row[0]] = row[0]
		finally:
			pass
			
		return json.dumps(toret, ensure_ascii=False)
	else:
		abort(make_response('No datas given !', 400))