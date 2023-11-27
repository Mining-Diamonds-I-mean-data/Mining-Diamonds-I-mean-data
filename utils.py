import csv
import os
import psycopg2
from typing import Iterable
from johnnydep import JohnnyDist
import requests
from bs4 import BeautifulSoup

database_password = os.environ.get("DATABASE_PASSWORD", "wrong password friend")
if database_password == "wrong password friend":
    raise NameError("You forgot to set the environment variable with a password 'export DATABASE_PASSWORD=abc123'")


# Function that gets database connection
def get_db_connection():
    conn = psycopg2.connect(database="postgres",
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
def get_library_release_versions(package_name):
    response_raw = ""
    url = "https://pypi.org/pypi/" + str(package_name.split("=")[0]) + "/json"
    try:
        response_raw = requests.get(url)
        response = response_raw.json()
        if "message" in response and response["message"] == "Not Found":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO package_does_not_exist_on_pypi (package) VALUES (%s);', (package_name,))
            conn.commit()
            conn.close()
            print("(fn)", get_library_release_versions.__name__, "This library doesn't exist", response_raw.text, "|",
                  url)
            exit(66)
        return collect_representative_versions([version for version in response["releases"]])
    except Exception as e:
        print("(fn)", get_library_release_versions.__name__, "error: ", e, "|", response_raw.text, "|", url)
        exit(144)


# process package
def process_new_or_update_library(package_name):
    if "==" in package_name:
        return {"error": "Remove version allocator"}
    conn = get_db_connection()
    cursor = conn.cursor()

    # get set difference to find library versions we still have to collect from pypi
    packages_pypi_versions_list = get_library_release_versions(package_name)
    cursor.execute('SELECT version FROM import_names WHERE package_name = %s', (package_name,))
    packages_database_versions_list = [version[0] for version in cursor.fetchall()]
    cursor.execute('SELECT version FROM failed_libraries WHERE package = %s', (package_name,))
    packages_database_versions_list += [version[0] for version in cursor.fetchall()]
    versions_list = list(set(packages_pypi_versions_list) - set(packages_database_versions_list))

    cursor.execute('SELECT * FROM packages WHERE package = %s', (package_name,))
    does_the_table_contain_this_package = cursor.fetchone()
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
    conn.close()


# get a list of all pypi packages we have to check
def get_list_of_new_pypi_and_database_packages():
    def get_pypi_simple_package_list():
        response = requests.get("https://pypi.org/simple/")
        soup = BeautifulSoup(response.content, features="html.parser")
        url_set = set()
        for url in soup.find_all('a'):
            url_set.add(url.text)
        return url_set

    conn = get_db_connection()
    cursor = conn.cursor()
    # get packages we already have in our database
    cursor.execute('SELECT package FROM packages')
    packages_in_database = [packages[0] for packages in cursor.fetchall()]
    # get libraries which don't exist anymore on pypi
    cursor.execute('SELECT package FROM package_does_not_exist_on_pypi')
    packages_which_no_longer_exist_on_pypi = [packages[0] for packages in cursor.fetchall()]
    conn.close()
    # combine pypi + database package list and remove pypi libraries which no longer exist to save time
    return list(
        set(get_pypi_simple_package_list()) + set(packages_in_database) - set(packages_which_no_longer_exist_on_pypi))


def dump_database_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM import_names')
    does_the_table_contain_this_import = cursor.fetchall()

    dump_of_database = [{"library": i[2], "release": i[3], "import_name": i[1]} for i in
                        does_the_table_contain_this_import]
    conn.close()

    with open('dump.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['library', 'release', 'import_name'])
        writer.writeheader()
        writer.writerows(dump_of_database)


if __name__ == '__main__':
    # test code here
    pass
