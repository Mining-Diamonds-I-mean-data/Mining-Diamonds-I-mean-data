import sqlite3
from johnnydep import JohnnyDist
import requests
from bs4 import BeautifulSoup
import pickle


# https://pypi.org/simple/

def get_db_connection():
    conn = sqlite3.connect('/home/kolby/Documents/GitHub/Mining-Diamonds-I-mean-data/diamonds.db')
    return conn


def get_import_name(packageName):
    def check_if_we_care(packageName):
        try:
            response = requests.get("https://libraries.io/api/Pypi/" + str(packageName.split("=")[0]) +"?api_key=96f6c6227c05020af5b777f5f6e0134c").json()
            print(response)
            if response["dependents_count"] > 0 and response["dependent_repos_count"] > 0:
                return True
            return False
        except Exception as e:
            print("error: ", e)
            return False

    importNames = []
    conn = get_db_connection()
    cursor = conn.cursor()
    post = cursor.execute('SELECT * FROM packages WHERE package = ?', [packageName]).fetchone()
    if post is None:
        if check_if_we_care(packageName):
            importNames = JohnnyDist(packageName).import_names
            if len(importNames) != 0:
                posts = cursor.execute('INSERT INTO packages (package) VALUES (?);', [packageName]).fetchone()
                for i in importNames:
                    posts = cursor.execute('INSERT INTO importNames (importName, packageName) VALUES (?, ?);',
                                           (i, packageName)).fetchone()
                conn.commit()
            else:
                importNames = {"error": "Library you requested doesn't exist"}
        else:
            importNames = {"error": "Library you requested doesn't meet the requirements for our program to be considered a library"}
    else:
        bob = cursor.execute('SELECT * FROM importNames WHERE packageName = ?', (packageName,)).fetchall()
        importNames = [i[1] for i in bob]
    conn.close()
    return importNames


def get_list_of_pypi_packages():
    def get_yesterday_data():
        url_set_old = set()
        try:
            with open('yesterday_set_data.yourmom', 'rb') as fp:
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
        with open('yesterday_set_data.yourmom', 'wb') as fp:
            pickle.dump(url_set, fp)

    url_yesterday_set = get_yesterday_data()
    url_today_set = get_today_data()
    get_set_diff = url_today_set - url_yesterday_set
    for package_name in get_set_diff:
        get_import_name(package_name)


print(get_import_name("discord.py"))
