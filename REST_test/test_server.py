#!/user/bin/python

import sys
import os

# -------------------------------------------------
#
# This script can be used for test server function
# There are all commands for each reassources
#
# To use this script you can have to run this command : python test_server.pu arg1 arg2
# arg1 is the HTTP method GET, POST, PUT or DELETE
# arg2 is the ressources name
# eg : python test_server.py GET conf returns all configurated inputs
#
# You have some JSON file with this script, these files containes some JSON data for POST and PUT method
#
# Enjoy ;)
#
# -------------------------------------------------

if str(sys.argv[1]) == "GET":

    # return all configurated inputs
    if (str(sys.argv[2])) == "conf":
        os.system('curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://localhost:5000/configurations')

    # return all forms
    elif (str(sys.argv[2])) == "forms":
        os.system('curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://localhost:5000/forms')

    # return form with ID
    elif (str(sys.argv[2])) == "formID":
        os.system('curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://localhost:5000/form/1')

    # return all keywords
    elif (str(sys.argv[2])) == "keyword":
        os.system('curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://localhost:5000/keywords')

    # return all unities
    elif (str(sys.argv[2])) == "unity":
        os.system('curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://localhost:5000/unities')

    elif (str(sys.argv[2])) == "linked":
        os.system('curl -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://localhost:5000/linked')

elif str(sys.argv[1]) == "POST":

    # Create a configurated input with configuraedInput.json file data
    if (str(sys.argv[2])) == "conf":
        os.system(' curl -H "Content-Type: application/json" -d @JSON/configuratedInput.json http://localhost:5000/configurations')

    # Create a form with form.json file data
    elif (str(sys.argv[2])) == "form":
        os.system(' curl -H "Content-Type: application/json" -d @JSON/form.json http://localhost:5000/forms')

elif str(sys.argv[1]) == "PUT":

    # Update form
    if (str(sys.argv[2])) == "form":
        os.system(' curl -X PUT -H "Content-Type: application/json" -d @JSON/formUpdate.json http://localhost:5000/forms/1')

    # Update form
    if (str(sys.argv[2])) == "form2":
        os.system(' curl -X PUT -H "Content-Type: application/json" -d @JSON/formUpdateWithRemovedInput.json http://localhost:5000/forms/1')

else:
    print("DELETE")
