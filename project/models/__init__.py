# -*- coding: utf8 -*-Follow


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import json
import urllib.parse

from .base import Base
from . import Form
from . import FormProperty
from . import Input
from . import InputProperty
from . import FormFile
from . import Language
from . import FormTrad
import os

# Database connexion
# We use pyodbc and SQL Server for the moment

absPathConfigFile = os.path.abspath( os.path.join(os.path.dirname(__file__),'../config/config.json'))

with open(absPathConfigFile, "r") as config:
    data = json.loads( config.read() )
sqlConnexion = data["sql"]["url"] if 'sql' in data and 'url' in data['sql'] else 'CASIMIR/formbuilder'
sqlConnexion = urllib.parse.quote_plus(sqlConnexion)
sqlConnexion = "mssql+pyodbc:///?odbc_connect=%s" % sqlConnexion

dbConfig = data['dbConfig']
# recycle conn every 10min to prevent SQLSERVER to fuck our otherwise forever active connection
engine = create_engine(sqlConnexion, pool_recycle=6000)
Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(bind=engine))

