# NS.UI.FormBuilder python server

The database SQL script are currently for SQL Server (TSQL).

## Install depedancies

Run :

    pip install -r requirements-txt --allow-external pyodbc --allow-unverified pyodbc

On windows it can be more difficult to install pyodbc, so the best way is to download the whl package [on this page](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc).

To install the whl package on windows :

    pip install pyodbc-3.0.10-cp34-none-win_amd64.whl

Depedancies :

* Flask-SQLAlchemy==2.0
* flask==0.10.1
* formbuilder==0.0
* itsdangerous==0.24
* jinja2==2.7.3
* markupsafe==0.23
* pyodbc==3.0.6
* sqlalchemy==0.9.8
* sqlautocode==0.7
* werkzeug==0.9.6
