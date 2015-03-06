# -*- coding: utf-8 -*-
# 
from flask import Flask
app = Flask('project')
app.debug = True
from project.controllers import *