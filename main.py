#!/usr/bin/env python3
import configparser
import sqlite3
import time

from flask import Flask, g, jsonify, redirect, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

config = configparser.ConfigParser()
config.read("config.ini")

DATABASE = config["database"]["file"]


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        cur = db.cursor()
        qry = open("create_table.sql", "r").read()
        cur.execute(qry)
        cur.close()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return redirect("/api")


@app.route("/api", methods=["POST", "GET"])
def api():
    if request.method == "GET":
        """return a list of users"""
        return jsonify(get_users())

    if request.method == "POST":
        """modify/update the user database"""
        client_users = request.get_json()
        merge_users(client_users)
        return jsonify(get_users())

def merge_users(client_users):
    """Compare and update users in the database via those from the client"""
    cur = get_db().cursor()
    for user in client_users:
        # Check if user exists
        cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE rowid = ?)", (user["id"],))
        exists = cur.fetchone()[0]
        
        if exists:
            # update our user
            print("USER ID EXISTS:", user["id"])
            cur.execute("UPDATE users SET name=?,balance=?,drink_count=?,last_update=?,transponder_hash=? WHERE rowid=?", (user["name"], user["balance"], user["drinkCount"], time.time(), user["hash"], user["id"]))
        else:
            print("Inserting user", user["name"])
            cur.execute("INSERT INTO users VALUES (?,?,?,?,?)", (user["name"], user["balance"], user["drinkCount"], user["lastUpdate"], user["hash"]))
    
    get_db().commit()

def get_users():
    """Return users as a JSON Array"""
    cur = get_db().cursor()
    cur.execute("SELECT rowid, * FROM users")
    results = cur.fetchall()
    array = []
    for result in results:
        array.append(
            {
                "id": result[0],
                "name": result[1],
                "balance": result[2],
                "drinkCount": result[3],
                "lastUpdate": result[4],
                "hash": result[5],
            }
        )
    return array


if __name__ == "__main__":
    app.run(debug=True)
