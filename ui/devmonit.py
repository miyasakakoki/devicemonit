#!/usr/bin/python3

from flask import Flask, request, g, send_from_directory, render_template, session, redirect, url_for, jsonify
from functools import wraps
import sqlite3
import os
import datetime

app = Flask(__name__)
app.config.from_object( __name__ )
app.config.update( dict(
	DATABASE = os.path.join( app.root_path, 'devmon.db' ),
	SECRET_KEY = 'devmonit',
	USERNAME = 'admin',
	PASSWORD = 'default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SECRET_KEY'] = os.urandom(24)

def condb():
	"""Connect to Database"""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv
def getdb():
	if not hasattr( g, 'sqlite_db' ):
		g.sqlite_db = condb()
	return g.sqlite_db

def initdb():
	db = getdb()
	with app.open_resource( 'schema.sql', mode='r' ) as f:
		db.cursor().executescript(f.read())
	db.commit()

def checklogin( email, password ):
	cur = getdb().cursor()
	cur.execute( "select * from User where email = ? and pass = ?;", (email,password) )
	ret = cur.fetchone()
	if ret is None:
		return {"stat":"None"}
	return {"stat":"OK", "uid":ret["uid"], "Name":ret["Name"] }

def login_required(f):
	@wraps(f)
	def decorated_function( *args, **kwargs ):
		if "uid" not in session:
			return redirect( url_for("login") )
		return f( *args, **kwargs )
	return decorated_function

@app.cli.command('initdb')
def initdb_command():
	"""initialzes  the database"""
	initdb()
	print( "The database initialized." )

@app.teardown_appcontext
def closedb(error):
	if hasattr( g, 'sqlite_db' ):
		g.sqlite_db.close()




@app.route( "/", methods=["GET"] )
def test():
	return "OK"

@app.route( "/login", methods=["GET"] )
def login_page():
	return render_template( 'login.html' )

@app.route( "/login", methods=["POST"] )
def login():
	if "uid" in session:
		return redirect( url_for( "dashboard" ) )
	f = request.form
	if "email" in f and len(f["email"]) > 2 and "password" in f and len(f["password"]) > 2:
		res = checklogin( email=f["email"], password=f["password"] )
		if res["stat"] == "OK":
			session["uid"] = res["uid"]
			session["Name"] = res["Name"]
			session["Date"] = datetime.datetime.now()
			return redirect( url_for("dashboard_page") )
	error = "Invalid credentials.Please try again."
	return render_template( 'login.html', error=error )

@app.route( "/logout" )
def logout():
	session.pop( "uid", None )
	return redirect( url_for( "login" ) )


@app.route( "/dashboard", methods=["GET"] )
@login_required
def dashboard_page():
	return render_template( 'dashboard.html', page="summary" )
#	return "UID:" + str(session["uid"]) + "   Name: "+ session["Name"] + "   Date:"+ session["Date"].strftime( "%y%m%d %H:%M:%s" )

@app.route( "/api/device/all" )
@login_required
def devicestatus_all():
	test = { "devices":[
		{"ID":"X1", "Stat":"OK", "Name":"one"},
		{"ID":"X2", "Stat":"NG", "Name":"two"},
		{"ID":"X3", "Stat":"UP", "Name":"three"},
		{"ID":"X4", "Stat":"OK", "Name":"four"}
	], "Time":"yyyymmdd hhmmss" }
	return jsonify( test )

@app.route( "/signup", methods=["GET"] )
def signup_page():
	return render_template( 'signup.html' )

@app.route( "/signup", methods=["POST"] )
def signup():
	t = request.get_json(force=True)
	return "OK"


@app.route('/<path:path>')
def send_js(path):
	return send_from_directory('statics', path)

if __name__ == "__main__":
	app.run()
