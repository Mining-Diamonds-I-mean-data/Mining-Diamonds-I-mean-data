import sqlite3
from johnnydep import JohnnyDist

# establish connection to database
def get_db_connection():
    conn = sqlite3.connect('C:\\Users\\maraf\\Documents\\499\Mining-Diamonds-I-mean-data\\diamonds.db')
    return conn

def get_import_name(packageName):

    ### TODO: validate package name before adding to database. can check if package is in PyPI or check if it has import names

    importNames = []
    conn = get_db_connection() # connect to database
    cursor = conn.cursor()
    # check if package is already in database
    post = cursor.execute('SELECT * FROM packages WHERE package = ?', [packageName]).fetchone()

    if post is None: # if package is not in database
        # get import names from JohnnyDist and add to database
        importNames = JohnnyDist(packageName).import_names
        posts = cursor.execute('INSERT INTO packages (package) VALUES (?);', [packageName]).fetchone()
        for i in importNames:
            posts = cursor.execute('INSERT INTO importNames (importName, packageName) VALUES (?, ?);', (i, packageName)).fetchone()
        conn.commit()
    else: # if package is in database
        # get import names from database
        bob = cursor.execute('SELECT importName FROM importNames WHERE packageName = ?', (packageName,)).fetchall()
        importNames = [i for i in bob]

    conn.close()
    return importNames