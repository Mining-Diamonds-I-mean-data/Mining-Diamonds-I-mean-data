import sqlite3
from flask import Flask, json, request
from johnnydep import JohnnyDist
from utils import *
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/packagename')
def package_to_import():
    packageName = request.args.get('packageName')
    # get import names and create json response
    importNames = get_import_name(packageName)
    response = app.response_class(
        response=json.dumps(importNames),
        mimetype='application/json'
    )
    return response

@app.route('/importname')
def import_to_package():
    importName = request.args.get('importName')

    packageNames = []
    conn = get_db_connection() # connect to database
    cursor = conn.cursor()
    # get the package name from the import name 
    bob = cursor.execute('SELECT packageName FROM importNames WHERE importName = ?', [importName]).fetchall()

    if bob: # if import name is in database
        packageNames = [i for i in bob]
        # create json response
        response = app.response_class(
            response=json.dumps(packageNames),
            mimetype='application/json'
        )
    else: # if import name is not in database
        response = app.response_class(
            response=json.dumps("import name not found"),
            mimetype='application/json'
        )
        
    conn.close()
    return response


if __name__ == '__main__':
    app.run()
