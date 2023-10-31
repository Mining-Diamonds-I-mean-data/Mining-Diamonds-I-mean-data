import itertools
import os
import random
from time import sleep

import psycopg2
from typing import Iterable

from johnnydep import JohnnyDist
import requests
from bs4 import BeautifulSoup
import pickle
from api_keys import api_keys

database_password = os.environ.get("DATABASE_PASSWORD", "wrong password pale")
if database_password == "wrong password pale":
    raise NameError("You forgot to set the environment variable with a passwork 'export DATABASE_PASSWORD=abc123'")

# Function that gets database connection
def get_db_connection():
    conn = psycopg2.connect(database="run2",
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
def check_if_we_care(package_name, api_key):
    response_raw = ""
    url = "https://libraries.io/api/Pypi/" + str(package_name.split("=")[0]) + "?api_key=" + api_key
    try:
        # put a sleep here so using the semaphore is a last resort
        sleep(1)
        response_raw = requests.get(url)
        response = response_raw.json()
        if "error" in response and response["error"] == "not found":
            print("(fn)", check_if_we_care.__name__, "This library doesn't exist", response_raw.text, "|", url)
            exit(66)
        if response["dependents_count"] > 0 and response["dependent_repos_count"] > 0:
            return True, collect_representative_versions([version["number"] for version in response["versions"]])
        return False, None
    except Exception as e:
        print("(fn)", check_if_we_care.__name__, "error: ", e, "|", response_raw.text, "|", url)
        exit(144)

# process package
def get_import_name(package_name, api_key):
    if "==" in package_name:
        return {"error": "Remove version allocator"}
    do_we_care_boolean, versions_list = check_if_we_care(package_name, api_key)

    if do_we_care_boolean:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM packages WHERE package = %s', (package_name,))
        does_the_table_contain_this_package = cursor.fetchone()
        print("hi", does_the_table_contain_this_package)
        if does_the_table_contain_this_package is None:
            cursor.execute('INSERT INTO packages (package) VALUES (%s);', (package_name,))
            conn.commit()
            for version in versions_list:
                try:
                    import_names = JohnnyDist(package_name + "==" + version).import_names
                    if len(import_names) != 0:
                        for i in import_names:
                            cursor.execute(
                                'INSERT INTO import_names (import_name, package_name, version) VALUES (%s, %s, %s);',
                                (i, package_name, version,))
                        conn.commit()
                    else:
                        print("error Library you requested doesn't exist")
                except Exception as e:
                    cursor.execute('INSERT INTO failed_libraries (package, version, reason) VALUES (%s, %s, %s);',
                                   (package_name, version, str(e),))
                    conn.commit()
                    print("Error: python package: " + package_name + " failed on version: " + version + " error:", e)
        else:
            cursor.execute('INSERT INTO packages_not_picked (package) VALUES (%s);', (package_name,))
            conn.commit()
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
    return get_set_diff

# update package dataset with new versions
def update_package_dataset():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT package FROM packages')
    packages = cursor.fetchall()
    round_robin = itertools.cycle(api_keys)
    for package in packages:
        package = package[0]
        do_we_care_boolean, versions_list = check_if_we_care(package, round_robin.__next__())
        if do_we_care_boolean:
            for version in reversed(versions_list):
                cursor.execute('SELECT * FROM import_names WHERE package_name = %s AND version = %s',
                                     (package, version,))
                found_result = cursor.fetchone()
                if found_result is None:
                    try:
                        import_names = JohnnyDist(package + "==" + version).import_names
                        if len(import_names) != 0:
                            for i in import_names:
                                cursor.execute(
                                    'INSERT INTO import_names (import_name, package_name, version) VALUES (%s, %s, %s);',
                                    (i, package, version,))
                            conn.commit()
                    except Exception as e:
                        cursor.execute('INSERT INTO failed_libraries (package, version, reason) VALUES (%s, %s, %s);',
                                       (package, version, str(e),))
                        conn.commit()
                        print("Error: python package: " + package + " failed on version: " + version + " error:", e)
                else:
                    break
    conn.close()


# run this every day to keep
def run_every_day():
    round_robin = itertools.cycle(api_keys)
    update_package_dataset()
    for package_name in get_list_of_pypi_packages():
        get_import_name(package_name, round_robin.__next__())

if __name__ == '__main__':
    # if you are running utils.py as a file this is to debug get_import_name
    def get_today_data():
        response = requests.get("https://pypi.org/simple/")
        soup = BeautifulSoup(response.content, features="html.parser")
        url_set = set()
        for url in soup.find_all('a'):
            url_set.add(url.text)
        return url_set
    print(len(get_today_data()))
