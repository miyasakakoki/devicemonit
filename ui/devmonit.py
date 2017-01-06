#!/usr/bin/python3

from flask import Flask, request, g, send_from_directory, render_template, session, redirect, url_for, jsonify
from functools import wraps
import sqlite3
from influxdb import InfluxDBClient
import string
import os
import datetime
import random

app = Flask(__name__)
app.config.from_object( __name__ )
app.config.update( dict(
	DATABASE = os.path.join( app.root_path, 'devmon.db' ),
	SECRET_KEY = 'devmonit',
	USERNAME = 'admin',
	PASSWORD = 'default',
	INFLUXDB = {
		"HOST": "localhost",
		"PORT": 8086,
		"USER": "test",
		"PASS": "mytestuser",
		"NAME": "devicemonit"
	}
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
#app.config['SECRET_KEY'] = os.urandom(24)
app.config['SECRET_KEY'] = "testkey"

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

def get_all( uid ):
	ifdb = app.config["INFLUXDB"]
	client = InfluxDBClient( ifdb["HOST"], ifdb["PORT"], ifdb["USER"], ifdb["PASS"], ifdb["NAME"] )
	cur = getdb().cursor()
	cur.execute( "select did, Name, Description from Devices where uid = ?;", (uid,) )
	result = cur.fetchall()
	ret = []
	if result is not None:
		for i in result:
			tmp = { "ID": i["did"], "Name": i["Name"], "Description": i["Description"] }
			rs = list(client.query( "select last(*) from \"{0}\";".format( i["did"] ), epoch="s" ).get_points())
			now = int(datetime.datetime.now().timestamp())
			if len(rs) == 0 or rs[0]["time"] == 0:
				tmp["Stat"] = "NG"
				tmp["time"] = "0"
			else:
				tmp["time"] = datetime.datetime.fromtimestamp( rs[0]["time"] ).strftime( "%Y/%m/%d %H:%M:%S" )
				print( tmp["time"] )
				tmp["Stat"] = "NG" if rs[0]["time"] < now-65 else "OK"
			ret.append( tmp )
	return ret

def checkdeviceid( did ):
	if did == None or len(did) < 8:
		return False
	for c in did:
		if c not in string.ascii_letters and c not in string.digits and c not in "_#":
			return False
	r = getdb().execute( "select * from devices where did = ?;", (did,) ).fetchone()
	return False if r is not None else True

def login_required(f):
	@wraps(f)
	def decorated_function( *args, **kwargs ):
		if "uid" not in session:
			return redirect( url_for("login") )
		session["Date"] = datetime.datetime.now()
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
		return redirect( url_for( "dashboard_page" ) )
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

@app.route( "/api/device/all" )
@login_required
def devicestatus_all():
	return jsonify( { "devices": get_all( session["uid"] ), "Time": session["Date"].strftime( "%Y/%m/%d %H:%M:%S" ) } )

@app.route( "/api/deviceID"	, methods=["GET"] )
@login_required
def gen_device_id():
	while True:
		tmp = "".join( random.SystemRandom().choice( string.ascii_letters + string.digits ) for _ in range(16) )
		result = getdb().cursor().execute( "select * from devices where did = ?;", (tmp,) ).fetchone()
		if result == None:
			break;
	return jsonify( {"ID":tmp} )

@app.route( "/api/deviceID" , methods=["POST"] )
@login_required
def check_device_id():
	return jsonify( { "stat": "OK" if checkdeviceid( request.json["ID"] ) else "NG" } )

@app.route( "/api/device/<DeviceID>", methods=["POST"] )
@login_required
def mod_device( DeviceID ):
	if request.json["stat"] == "new":
		if checkdeviceid(DeviceID):
			db = getdb()
			db.execute( "insert into devices( uid, did, Name, Description ) values(?,?,?,?);", (session["uid"], DeviceID, request.json["Name"], request.json["Description"] ) )
			db.commit()
			ifdb = app.config["INFLUXDB"]
			client = InfluxDBClient( ifdb["HOST"], ifdb["PORT"], ifdb["USER"], ifdb["PASS"], ifdb["NAME"] )
			client.write_points( [{"measurement":DeviceID, "tags":{}, "time":0, "fields":{"Stat":"None"}}] )
			return jsonify( {"stat":"OK"} )
		return jsonify( {"stat":"NG"} )
	else:
		db = getdb()
		db.execute( "update devices set Name = ?, Description = ? where did = ?;", (request.json["Name"], request.json["Description"], DeviceID ) )
		db.commit()
		return jsonify( {"stat":"OK"} )

@app.route( "/api/device/<DeviceID>", methods=["DELETE"] )
@login_required
def del_device( DeviceID ):
	db = getdb()
	db.execute( "delete from devices where did = ?;", (DeviceID,) )
	db.commit()
	ifdb = app.config["INFLUXDB"]
	client = InfluxDBClient( ifdb["HOST"], ifdb["PORT"], ifdb["USER"], ifdb["PASS"], ifdb["NAME"] )
	client.query( "Drop measurement \"{0}\";".format( DeviceID ) )
	return jsonify( {"stat":"OK"} )

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
