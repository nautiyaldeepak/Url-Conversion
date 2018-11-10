import os
import re
import hashlib
import base64

import mysql.connector
from flask import Flask, render_template, request

BASE_URL = 'http://miniurl.com/'


def create_unique_key():
    unique_key = str(base64.urlsafe_b64encode(hashlib.md5(os.urandom(128)).digest())[:8])
    unique_key = unique_key[2:len(unique_key) - 1]
    return unique_key


mydb = mysql.connector.connect(
    host="database_host_here",
    user="database_user_here",
    passwd="password_here",
    database="database_name_here"
)

mycursor = mydb.cursor()
app = Flask(__name__)


def checkTable():
    check = 0
    mycursor.execute("SHOW TABLES")
    for tb in mycursor:
        if str(tb[0]) == "bytearray(b'urlshort')":
            check = 1
    if check == 0:
        mycursor.execute("CREATE TABLE urlshort (uid VARCHAR(8), long_url VARCHAR(200), short_url VARCHAR(28))")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create')
def create_short_url():
    checkTable()
    key = create_unique_key()
    user_input = request.args.get('long_url')

    if not re.match("^http[s]?\:\/\/.*\..*", user_input):
        return render_template('index.html', shortUrl='"{}": Not a valid URL'.format(user_input))

    sqlFormula = "SELECT long_url, short_url FROM urlshort WHERE long_url = %s"
    mycursor.execute(sqlFormula, (user_input,))
    try:
        result = mycursor.fetchall()
        if result[0][0] == user_input:
            return render_template('index.html', shortUrl='Short url already exists: ' + result[0][1])
    except:
        print("No entry found")
    sqlFormula = "INSERT INTO urlshort (uid, long_url, short_url) VALUES (%s, %s, %s)"
    entryData = (key, user_input, BASE_URL + key)
    mycursor.execute(sqlFormula, entryData)
    mydb.commit()
    return render_template('index.html', shortUrl='Short url created: ' + BASE_URL + key)


@app.route('/extract')
def get_long_url():
    user_input = request.args.get('short_url')
    sqlFormula = "SELECT long_url FROM urlshort WHERE short_url = %s"
    mycursor.execute(sqlFormula, (user_input,))
    result = mycursor.fetchone()
    if result is None:
        return render_template('index.html', longUrl='Does not exist')
    else:
        return render_template('index.html', longUrl='Long url is: ' + result[0])


if __name__ == '__main__':
    app.run(port=4000)
