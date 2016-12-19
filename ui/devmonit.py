


from flask import Flask, request
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

@app.route( "/", methods=["GET"] )
def login_page():
	return loginpage

if __ name__ == "__main__":
	app.run()
