import sqlite3
from johnnydep import JohnnyDist

def get_db_connection():
    conn = sqlite3.connect('/home/kolby/Documents/GitHub/Mining-Diamonds-I-mean-data/diamonds.db')
    return conn

def get_import_name(packageName):
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
        importNames = [i[1] for i in bob]
    conn.close()
    return importNames