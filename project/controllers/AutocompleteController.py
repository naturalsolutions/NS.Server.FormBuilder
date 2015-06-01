# -*- coding: utf-8 -*-
# 
from project import app
from ..models import session
from ..models.Form import Form
import json

# Return all forms
@app.route('/autocomplete/forms', methods = ['GET'])
def getFormName():
    query = session.query(Form.name).all()

    forms = []
    for eachInput in query:
        forms.append(eachInput[0])

    return json.dumps({"options":forms})