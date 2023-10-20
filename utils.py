import os

import psycopg2
from typing import Iterable

from johnnydep import JohnnyDist
import requests
from bs4 import BeautifulSoup
import pickle

database_password = os.environ.get("DATABASE_PASSWORD", "wrong password pale")
if database_password == "wrong password pale":
    raise NameError("You forgot to set the environment variable with a passwork 'export DATABASE_PASSWORD=abc123'")


# Function that gets database connection
def get_db_connection():
    conn = psycopg2.connect(database="db_name",
                        host="localhost",
                        user="postgres",
                        password=database_password,
                        port="5432")
    return conn

def collect_representative_versions(lib_versions: Iterable[str]):
    minors = set()
    versions_to_keep = set()
    for version in lib_versions:
        version_split = version.split(".")
        minor = version_split[0]
        if len(version_split) > 1:
            minor += ("." + version_split[1])
        if minor not in minors:
            minors.add(minor)
            versions_to_keep.add(version)
            continue
    versions_to_keep = list(versions_to_keep)
    versions_to_keep.sort()
    return versions_to_keep

# check if package fits within criteria and if it does return the versions to process
def check_if_we_care(packageName):
    try:
        response = requests.get("https://libraries.io/api/Pypi/" + str(
            packageName.split("=")[0]) + "?api_key=96f6c6227c05020af5b777f5f6e0134c").json()
        if response["dependents_count"] > 0 and response["dependent_repos_count"] > 0:
            return True, collect_representative_versions([version["number"] for version in response["versions"]])
        return False, None
    except Exception as e:
        print("error: ", e)
        return False, None

# process package
def get_import_name(packageName):
    if "==" in packageName:
        return {"error": "Remove version allocator"}

    importNames = []
    conn = get_db_connection()
    cursor = conn.cursor()
    does_the_table_contain_this_package = cursor.execute('SELECT * FROM packages WHERE package = ?',
                                                         [packageName]).fetchone()

    print("hi", does_the_table_contain_this_package)
    if does_the_table_contain_this_package is None:
        do_we_care_boolean, versions_list = check_if_we_care(packageName)
        if do_we_care_boolean:
            cursor.execute('INSERT INTO packages (package) VALUES (?);', [packageName]).fetchone()
            for version in versions_list:
                try:
                    importNames = JohnnyDist(packageName + "==" + version).import_names
                    if len(importNames) != 0:
                        for i in importNames:
                            cursor.execute(
                                'INSERT INTO importNames (importName, packageName, version) VALUES (?, ?, ?);',
                                (i, packageName, version)).fetchone()
                        conn.commit()
                    else:
                        print("error Library you requested doesn't exist")
                except Exception as e:
                    cursor.execute('INSERT INTO crying_junk (package, version, reason) VALUES (?, ?, ?);',
                                   (packageName, version, str(e))).fetchone()
                    conn.commit()
                    print("Error: python package: " + packageName + " failed on version: " + version + " error:", e)
    conn.close()

# gets a list of pypi packages we didn't process today and processes them

def get_list_of_pypi_packages():
    def get_yesterday_data():
        url_set_old = set()
        try:
            with open('yesterday_set.pickle', 'rb') as fp:
                url_set_old = pickle.load(fp)
        except:
            pass
        return url_set_old

    def get_today_data():
        response = requests.get("https://pypi.org/simple/")
        soup = BeautifulSoup(response.content, features="html.parser")
        url_set = set()
        for url in soup.find_all('a'):
            url_set.add(url.text)
        dump_todays_data(url_set)
        return url_set

    def dump_todays_data(url_set):
        with open('yesterday_set.pickle', 'wb') as fp:
            pickle.dump(url_set, fp)

    url_yesterday_set = get_yesterday_data()
    url_today_set = get_today_data()
    get_set_diff = url_today_set - url_yesterday_set
    for package_name in get_set_diff:
        get_import_name(package_name)

# update package dataset with new versions
def update_package_dataset():
    importNames = []
    conn = get_db_connection()
    cursor = conn.cursor()

    packages = cursor.execute('SELECT package FROM packages').fetchall()

    for package in packages:
        package = package[0]
        do_we_care_boolean, versions_list = check_if_we_care(package)
        if do_we_care_boolean:
            for version in reversed(versions_list):
                found_result = cursor.execute('SELECT * FROM importNames WHERE packageName = ? AND version = ?',
                                     [package, version]).fetchone()
                if found_result is None:
                    try:
                        importNames = JohnnyDist(package + "==" + version).import_names
                        if len(importNames) != 0:
                            for i in importNames:
                                cursor.execute(
                                    'INSERT INTO importNames (importName, packageName, version) VALUES (?, ?, ?);',
                                    (i, package, version)).fetchone()
                            conn.commit()
                    except Exception as e:
                        cursor.execute('INSERT INTO crying_junk (package, version, reason) VALUES (?, ?, ?);',
                                       (package, version, str(e))).fetchone()
                        conn.commit()
                        print("Error: python package: " + package + " failed on version: " + version + " error:", e)
                else:
                    break
    conn.close()


# run this every day to keep
def run_every_day():
    update_package_dataset()
    get_list_of_pypi_packages()
