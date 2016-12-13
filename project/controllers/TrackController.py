# -*- coding: utf-8 -*-
#
from project import app
from flask import jsonify, abort, render_template, request, make_response
from ..utilities import Utility
from ..models import session, engine
from sqlalchemy import *
import urllib.parse
import json
import sys
import datetime
import pprint

def getTrackSqlConnection():
	with open ("project/config/config.json", "r") as myfile:
		data = json.loads(myfile.read())

	trackSqlConnexion = data["sql"]["urlTrack"] if 'sql' in data and 'urlTrack' in data['sql'] else abort(make_response('config.json file has no url referencing Track Database !', 400))
	trackSqlConnexion = urllib.parse.quote_plus(trackSqlConnexion)
	trackSqlConnexion = "mssql+pyodbc:///?odbc_connect=%s" % trackSqlConnexion

	print("trackSqlConnexion = " + trackSqlConnexion)
	try:
		trackEngine = create_engine(trackSqlConnexion)
	except e as Exception:
		abort(make_response('Could not open database !', 400))
	else:
		return trackEngine
	finally:
		pass

	return None

@app.route('/Track/getData', methods = ['POST'])
def getData():
	if 'datas' in request.json:
		toret = {}
		trackEngine = getTrackSqlConnection()

		if (trackEngine != None):
			for dataType in request.json["datas"]:
				toret[dataType] = {}
				result = trackEngine.execute("SELECT DISTINCT [TPro_"+dataType+"] FROM [TProtocole]")
				for row in result:
					toret[dataType][row[0]] = row[0]
			return json.dumps(toret, ensure_ascii=False)
	else:
		abort(make_response('No datas given !', 400))

@app.route('/getTrackUnities/<string:lang>', methods = ['GET'])
def getTrackUnities(lang):
	toret = {}
	trackEngine = getTrackSqlConnection()

	if (trackEngine != None):
		toret["unities"] = []
		result = trackEngine.execute("SELECT DISTINCT [TUni_Label"+lang+"] FROM [TUnite] ORDER BY [TUni_Label"+lang+"]")
		for row in result:
			toret["unities"].append(row[0])
		return json.dumps(toret, ensure_ascii=False)

@app.route('/TrackTypes/<string:lang>', methods = ['GET'])
def getTrackTypes(lang):
	toret = {}
	trackEngine = getTrackSqlConnection()

	if (trackEngine != None):
		toret["types"] = []
		result = trackEngine.execute("SELECT DISTINCT [TTyp_Nom_Label"+lang+"] FROM [TType] ORDER BY [TTyp_Nom_Label"+lang+"]")
		for row in result:
			toret["types"].append(row[0])
		return json.dumps(toret, ensure_ascii=False)

