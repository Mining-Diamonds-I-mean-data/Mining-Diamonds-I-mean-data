from flask import Flask, json, request
from utils import *

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# http://127.0.0.1:5000/library/discord.py:0.11.0,setuptools
@app.route('/library/<string:packages>')
def package_to_import(packages):
    conn = get_db_connection()
    cursor = conn.cursor()

    packages_json_list = {"result": [], "error": []}
    for package in packages.split(','):
        package = package.split(':')
        package_name = package[0]
        package_version = ""

        does_the_table_contain_this_package = cursor.execute('SELECT * FROM packages WHERE package = ?',
                                                             [package_name]).fetchone()
        if does_the_table_contain_this_package is None:
            packages_json_list["error"].append(
                package_name + " OptionalVersion(" + package_version + ") isn't include in the dataset")
        else:
            if len(package) > 1:
                package_version = package[1]
                found_package = cursor.execute('SELECT * FROM importNames WHERE packageName = ? AND version = ?',
                                               (package_name, package_version,)).fetchall()
            else:
                found_package = cursor.execute('SELECT * FROM importNames WHERE packageName = ?',
                                               (package_name,)).fetchall()
            packages_json_list["result"].extend(
                [{"import_name": i[1], "library_name": i[2], "version": i[3]} for i in found_package])
    conn.close()

    response = app.response_class(
        response=json.dumps(packages_json_list),
        mimetype='application/json'
    )
    return response


# http://127.0.0.1:5000/importname/discord,pkg_resources
@app.route('/importname/<string:imports>')
def import_to_package(imports):
    conn = get_db_connection()
    cursor = conn.cursor()

    imports_json_list = {"result": [], "error": []}
    for import_name in imports.split(','):
        if ':' in import_name:
            imports_json_list["error"].append(
                "The import name provided: " + import_name + " contains a ':' which is invalid")
            continue

        does_the_table_contain_this_import = cursor.execute('SELECT * FROM importNames WHERE importName = ?',
                                                            [import_name]).fetchall()
        if does_the_table_contain_this_import is None:
            imports_json_list["error"].append(
                "The import name provided: " + import_name + " isn't contained in our database")
        else:
            imports_json_list["result"].extend([{"import_name": i[1], "library_name": i[2], "version": i[3]} for i in
                                                does_the_table_contain_this_import])
    conn.close()

    response = app.response_class(
        response=json.dumps(imports_json_list),
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run()
