import sqlite3
from flask import Flask, json, request
from johnnydep import JohnnyDist
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('/home/kolby/Documents/GitHub/Mining-Diamonds-I-mean-data/diamonds.db')
    return conn

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/packagename')
def package_to_import():
    packageName = request.args.get('packageName')

    importNames = []
    conn = get_db_connection()
    cursor = conn.cursor()
    post = cursor.execute('SELECT * FROM packages WHERE package = ?', [packageName]).fetchone()
    if post is None:
        importNames = JohnnyDist(packageName).import_names
        posts = cursor.execute('INSERT INTO packages (package) VALUES (?);', [packageName]).fetchone()
        for i in importNames:
            posts = cursor.execute('INSERT INTO importNames (importName, packageName) VALUES (?, ?);', (i, packageName)).fetchone()
        conn.commit()
    else:
        bob = cursor.execute('SELECT * FROM importNames WHERE packageName = ?', (packageName,)).fetchall()
        importNames = bob
    conn.close()
    response = app.response_class(
        response=json.dumps(importNames),
        mimetype='application/json'
    )
    return response

@app.route('/importname')
def import_to_package():
    packageName = request.args.get('importName')

    importNames = []
    conn = get_db_connection()
    cursor = conn.cursor()
    post = cursor.execute('SELECT * FROM packages WHERE package = ?', [packageName]).fetchone()
    if post is None:
        importNames = JohnnyDist(packageName).import_names
        posts = cursor.execute('INSERT INTO packages (package) VALUES (?);', [packageName]).fetchone()
        for i in importNames:
            posts = cursor.execute('INSERT INTO importNames (importName, packageName) VALUES (?, ?);', (i, packageName)).fetchone()
        conn.commit()
    else:
        bob = cursor.execute('SELECT * FROM importNames WHERE packageName = ?', (packageName,)).fetchall()
        importNames = bob
    conn.close()
    response = app.response_class(
        response=json.dumps(importNames),
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run()
