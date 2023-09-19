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
    conn = get_db_connection()
    cursor = conn.cursor()
    bob = cursor.execute('SELECT * FROM importNames WHERE importName = ?', [importName]).fetchall()
    packageNames = [i[2] for i in bob]
    conn.close()
    response = app.response_class(
        response=json.dumps(packageNames),
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run()
