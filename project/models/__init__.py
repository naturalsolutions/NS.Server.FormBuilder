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
from . import Unity
from . import Propagation
from . import FormFile
from . import ConfiguratedInput
from . import ConfiguratedInputProperty
from . import Fieldset
from . import Language
from . import FormTrad


# Database connexion
# We use pyodbc and SQL Server for the moment
with open("project/config/config.json", "r") as config:
    data = json.loads( config.read() )
sqlConnexion = data["sql"]["url"] if 'sql' in data and 'url' in data['sql'] else 'CASIMIR/formbuilder'
sqlConnexion = urllib.parse.quote_plus(sqlConnexion)
sqlConnexion = "mssql+pyodbc:///?odbc_connect=%s" % sqlConnexion

dbConfig = data['dbConfig']
engine = create_engine(sqlConnexion)
Base.metadata.create_all(engine)
session = scoped_session(sessionmaker(bind=engine))

