# -*- coding: utf-8 -*-
#
from project import app
from flask import abort, request, make_response
from ..models import session
from ..models.Form import Form
from ..models.Input import Input
from sqlalchemy import *
from sqlalchemy.exc import ProgrammingError
import urllib.parse
import json


def getPositionSqlConnection(forcedSqlConn = None):
	if forcedSqlConn != None:
		positionSqlConnexion = forcedSqlConn
	else:
		with open ("project/config/config.json", "r") as myfile:
			data = json.loads(myfile.read())

		positionSqlConnexion = data["sql"]["urlPosition"] if 'sql' in data and 'urlPosition' in data['sql'] else abort(make_response('config.json file has no url referencing a Referential Position Database !', 400))
		positionSqlConnexion = urllib.parse.quote_plus(positionSqlConnexion)
		positionSqlConnexion = "mssql+pyodbc:///?odbc_connect=%s" % positionSqlConnexion

	#print("positionSqlConnexion = " + positionSqlConnexion)
	try:
		positionEngine = create_engine(positionSqlConnexion)
	except ProgrammingError:
		abort(make_response('Could not open database !', 400))
	else:
		return positionEngine
	finally:
		pass

	return None


# USELESS FOR NOW ... USE DIRECT CALL TO POSITION INSTEAD THROUGH WEBSERVICES
@app.route('/PositionTypes/<string:lang>', methods = ['GET'])
def getPositionTypes(lang):
	toret = {}
	positionEngine = getTrackSqlConnection()

	if (False and positionEngine != None):
		toret["types"] = []
		result = positionEngine.execute("???")
		for row in result:
			toret["types"].append(row[0])
		return json.dumps(toret, ensure_ascii=False)

