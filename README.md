# FormBuilder Back-End

What does the Back of the Formbuilder needs to work ?
-----

- python 3
- pip
- sql server
- iis

--------------------------------------------------

Installation
-----

Clone the repository

	git clone https://github.com/NaturalSolutions/NS.Server.FormBuilder.git

Install dependancies

    pip install -r requirements-txt --allow-external pyodbc --allow-unverified pyodbc

On windows it can be more difficult to install pyodbc, so the best way is to download the whl package [on this page](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc).

Install the whl package

    pip install pyodbcPackageYouDownloaded.whl

--------------------------------------------------

Configuration
-----

Rename and edit the **config.example.json** configuration file

	project/config/config.example.json

into

	project/config/config.json

You'll have to rewrite the connections string "url" in the "sql" index
For that, you have an example visible in this file at the "_comment" option

	"_comment" : "DRIVER={SQL Server};Server=.;Database=TRACK_DEV;UID=FormBuilderUser;PWD=fbuser42;"

*Ignore the options you know nothing about*

--------------------------------------------------

Database
-----

In sql Server, create the formbuilder database with the name you indicated in the connection string in your config.json file

*Do not forget to properly set the user rights, again as indicated in the config.json file connection string*


The database elements will be automatically created at the first launch of the server


--------------------------------------------------
IIS
-----

You must create a reverse proxy in your IIS server
Your clients will point at this reverse proxy to reach your server

You may want to have it's options look like this

	Model : FormbuilderWS/(.*)

and

	URL Rewrite : http://localhost:5000/{R:1}


--------------------------------------------------

Launch
-----

Launch your server from the root repository with the command

	python runserver.py
