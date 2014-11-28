# -*- coding: utf-8 -*-
from project                import app
from flask                  import jsonify, abort, render_template
from ..models import Session
from ..models.repositoryDB  import Protocol, Unity, Keyword, Version, Configuration
from ..utility.utility      import XMLUtiliy
from ..utility.protocolUtility      import ProtocolUtility
from sqlalchemy             import create_engine
from sqlalchemy.orm         import sessionmaker

import os

# Return all unit values
@app.route('/unities', methods = ['GET'])
def getUnities():
    unities = Session.query(Unity).all()
    un   = []
    for each in unities:
        un.append( each.text )
    return jsonify ({ "options" : un })


# Return a list of protocols name
# Used for javascript autocomplete source
@app.route('/protocols', methods = ['GET'])
def getProtocols():
    protos      = Session.query(Protocol).all()
    protocols   = []
    for each in protos :
        protocols.append( each.name )
    return jsonify({ "options" : protocols})


# return a list a keyword values
# Used for javascript autocomplete source
@app.route('/keywords', methods = ['GET'])
def getKeywords():
    keywords = Session.query(Keyword).all()
    ks   = []
    for each in keywords:
        ks.append( each.text.decode('latin-1').encode("utf-8") )
    return jsonify ({ "options" : ks })

# Get protocol by name
@app.route('/protocols/<name>', methods = ['GET'])
def getProtocolsByName(name):
    path = ProtocolUtility.XMLRepository + name;
    if os.path.isdir (path) and os.listdir (path):
        # get newest file
        newest = max (glob.iglob (path + '/*.xml'), key = os.path.getctime)
        return jsonify({ name : open(newest, 'r').read() })
    else:
        abort (404, 'No XML corresponding to specified name')


# POST routes, create a form with name and content
@app.route('/protocols', methods = ['POST'])
def createProtocole():
    if not request.json:
        abort(make_response('Data seems not be in ' + format +' format', 400))
    elif not 'name' in request.json or not 'content' in request.json or not 'comment' in request.json:
        abort(make_response('Some parameters are missing', 400))
    else:
        #check XML content
        self._checkXML (request.json['content'])

        # get current datetime
        current = datetime.today()
        # check if a protocol with this name yet exists
        proto = Session.query(Protocol).filter(Protocol.name == request.json['name']).first()

        if proto == None :
            proto   = Protocol (request.json['name'], request.json['description'], ProtocolUtility.XMLRepository + request.json['name'])

        ProtocolUtility.writeProtocol (request.json['name'], request.json['content'], current.strftime("%Y-%m-%d_%H-%M-%S"))

        # add a version to new protocol
        version = Version (request.json['comment'], current)
        proto.addVersion(version)

        # keywords
        keywordsList = request.json['keywords'].split(',');
        for each in keywordsList :
            proto.addKeyword( Keyword(each) )
        try:
            Session.add (proto)
            Session.commit ()
        except:
            Session.rollback()
        resp = jsonify({"proto" : proto.serialize()})
        return resp


# PUT routes, update protocol
@app.route('/protocols/<int:id>', methods=['PUT'])
def updateProtocol(id):
    if not request.json:
        self.wrongFormat('JSON')
    elif not 'content' in request.json:
        self.missingParameters()
    else:
        proto = self._session.query(Protocol).filter(Protocol.id == id).first()
        if proto != None:

            # write xml file
            current = datetime.datetime.now()
            path    = self._writeProtocol (proto.name, request.json['content'], current.strftime("%Y-%m-%d_%H-%M-%S"))
            version = Version (request.json['comment'], current)
            proto.versions.append (version)

            self._session.commit()
            return jsonify({"proto" : proto.serialize()})
        else:
            self.notFound()

@app.route('/configurations', methods = ['GET'])
def getConfiguration():
    configuration    = Session.query(Configuration).all()
    configurations   = []
    for each in configuration :
        configurations.append( each.type )
    return jsonify({ "options" : configurations})

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html')




