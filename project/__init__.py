# -*- coding: utf-8 -*-
# 
from flask import Flask
from .models import session

app = Flask('project')
app.debug = True
app.config['SQLALCHEMY_ECHO'] = True

@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()

from project.controllers import *