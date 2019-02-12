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


def getTrackSqlConnection(forcedSqlConn = None):
	if forcedSqlConn != None:
		trackSqlConnexion = forcedSqlConn
	else:
		with open ("project/config/config.json", "r") as myfile:
			data = json.loads(myfile.read())

		trackSqlConnexion = data["sql"]["urlTrack"] if 'sql' in data and 'urlTrack' in data['sql'] else abort(make_response('config.json file has no url referencing a Referential Track Database !', 400))
		trackSqlConnexion = urllib.parse.quote_plus(trackSqlConnexion)
		trackSqlConnexion = "mssql+pyodbc:///?odbc_connect=%s" % trackSqlConnexion

	#print("trackSqlConnexion = " + trackSqlConnexion)
	try:
		trackEngine = create_engine(trackSqlConnexion)
	except ProgrammingError:
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
			for key, value in request.json["datas"].items():
				toret[key] = {}
				table, column = value.split(":")
				result = trackEngine.execute("SELECT DISTINCT ["+table[:4]+"_"+column+"] FROM ["+table+"]")
				for row in result:
					toret[key][row[0]] = row[0]
			return json.dumps(toret, ensure_ascii=False)
	else:
		abort(make_response('No datas given !', 400))

@app.route('/unities/<string:context>/<string:lang>', methods = ['GET'])
@app.route('/getTrackUnities/<string:lang>', methods = ['GET'])
def getTrackUnities(lang, context):
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


@app.route('/Track/FormWeightWFBID/<int:formbuilderID>', methods = ['GET'])
def getTrackFormWeightWFBID(formbuilderID):
	myForm = session.query(Form).filter_by(pk_Form = formbuilderID).first()
	if myForm != None:
		return (getTrackFormWeight(myForm.originalID))
	else:
		abort(make_response('The form with ID ' + formbuilderID + ' could not be found !', 400))

@app.route('/Track/FormWeight/<int:originalID>', methods = ['GET'])
def getTrackFormWeight(originalID):
	toret = {}

	with open ("project/config/config.json", "r") as myfile:
		data = json.loads(myfile.read())

	trackDatabases = data["refsDB"]["track"] if 'refsDB' in data and 'track' in data['refsDB'] else abort(make_response('config.json file is incomplete and not referencing any Track Databases !', 400))

	toret["FormWeight"] = {}
	for itemDB in trackDatabases:
		trackSqlConnexion = "DRIVER={SQL Server};Server=TRACK\CORE;Database=" + itemDB + ";UID=FormBuilderUser;PWD=fbuser42;"
		trackSqlConnexion = urllib.parse.quote_plus(trackSqlConnexion)
		trackSqlConnexion = "mssql+pyodbc:///?odbc_connect=%s" % trackSqlConnexion

		trackEngine = getTrackSqlConnection(trackSqlConnexion)

		if (trackEngine != None):
			try:
				result = trackEngine.execute("SELECT count(*) FROM [TSaisie] WHERE TSai_FK_TPro_ID = " + str(originalID))
			except ProgrammingError:
				abort(make_response('Could not open database ' + itemDB + ' ! You might not have the proper rights ? Or the Database is missreferenced ?', 400))

			toret["FormWeight"][itemDB] = result.fetchone()[0]

	return json.dumps(toret, ensure_ascii=False)

@app.route('/Track/InputWeightWFBID/<int:formbuilderID>', methods = ['GET'])
def getTrackInputWeightWFBID(formbuilderID):
	myInput = session.query(Input).filter_by(pk_Input = formbuilderID).first()
	if myInput != None:
		return (getTrackInputWeight(myInput.originalID))
	else:
		abort(make_response('The input with ID ' + formbuilderID + ' could not be found !', 400))

@app.route('/Track/InputWeight/<int:originalID>', methods = ['GET'])
def getTrackInputWeight(originalID):
	toret = {}

	with open ("project/config/config.json", "r") as myfile:
		data = json.loads(myfile.read())

	trackDatabases = data["refsDB"]["track"] if 'refsDB' in data and 'track' in data['refsDB'] else abort(make_response('config.json file is incomplete and not referencing any Track Databases !', 400))

	toret["InputWeight"] = {}
	for itemDB in trackDatabases:
		trackSqlConnexion = "DRIVER={SQL Server};Server=TRACK\CORE;Database=" + itemDB + ";UID=FormBuilderUser;PWD=fbuser42;"
		trackSqlConnexion = urllib.parse.quote_plus(trackSqlConnexion)
		trackSqlConnexion = "mssql+pyodbc:///?odbc_connect=%s" % trackSqlConnexion

		trackEngine = getTrackSqlConnection(trackSqlConnexion)

		if (trackEngine != None):
			try:
				totresult = 0

				totresult = trackEngine.execute("SELECT count(*) from [TDChar] where TDCh_FK_TObs_ID = " + str(originalID)).fetchone()[0]
				
				if (totresult == 0):
					totresult = trackEngine.execute("SELECT count(*) from [TDEntier] where TDEn_FK_TObs_ID = " + str(originalID)).fetchone()[0]

				if (totresult == 0):
					totresult = trackEngine.execute("SELECT count(*) from [TDDate] where TDDa_FK_TObs_ID = " + str(originalID)).fetchone()[0]
				
				if (totresult == 0):
					totresult = trackEngine.execute("SELECT count(*) from [TDReel] where TDRe_FK_TObs_ID = " + str(originalID)).fetchone()[0]
			
			except ProgrammingError:
				abort(make_response('Could not open database ' + itemDB + ' ! You might not have the proper rights ? Or the Database is missreferenced ?', 400))

			toret["InputWeight"][itemDB] = totresult

	return json.dumps(toret, ensure_ascii=False)
