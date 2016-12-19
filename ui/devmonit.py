#!/usr/bin/python3

from flask import Flask, request, g
import sqlite3
import os

app = Flask(__name__)
app.config.from_object( __name__ )
app.config.update( dict(
	DATABASE = os.path.join( app.root_path, 'devmon.db' ),
	SECRET_KEY = 'devmonit',
	USERNAME = 'admin',
	PASSWORD = 'default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

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
def login_page():
	return loginpage

if __name__ == "__main__":
	app.run()
