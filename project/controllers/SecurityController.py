# -*- coding: utf-8 -*-
#
from project import app
from flask import jsonify, abort, request, make_response
import jwt

@app.route('/Security/isCookieValid', methods = ['POST'])
def isCookieValid():
	# this ensure request.json is read at least once.
	# it turns out that IIS tries to be fancy: if you don't access request.json for reading
	# on a POST request, it disregards any response from server and serves a 502 to client instead..
	if not request.json:
		abort(make_response('No json payload', 400))

	if 'ecoReleve-Core' not in request.cookies:
		abort(make_response('No reneco cookie in request', 400))

	if 'securityKey' not in request.json:
		abort(make_response('No security key provided', 400))

	try:
		decoded = jwt.decode(request.cookies['ecoReleve-Core'], verify=False)
	except:
		abort(make_response('Error decoding reneco cookie', 400))

	return (jsonify(decoded))
