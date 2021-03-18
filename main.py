#!/usr/bin/env python3
from flask import Flask, jsonify, redirect, request, g
from flask_cors import CORS
import configparser
import sqlite3

app = Flask(__name__)
CORS(app)

test = {
            "name": "Johannes Arnold",
            "drinkCount": 42,
            "balance": 9000,
            "lastUpdate": 1614867820842
        }

config = configparser.ConfigParser()
config.read('config.ini')

DATABASE = config['database']['file']

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return redirect("/api")

@app.route('/api', methods = ['POST', 'GET'])
def api():
    if request.method == 'GET':
        """return a list of users"""
        return jsonify([test])
    
    if request.method == 'POST':
        """modify/update the user database"""
        return jsonify("OK")

if __name__ == '__main__':
    app.run(debug=True)
    con = sqlite3.connect('coffee.db')
