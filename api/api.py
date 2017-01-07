#!/usr/bin/python3

import falcon
from influxdb import InfluxDBClient
import MYSQLdb
import time
import json

host='localhost'
port=8086
user='test'
password='mytestuser'
dbname='devicemonit'

def test():
	con = MYSQLdb.connect(
		user='UserName',
		passwd='Password',
		host='localhost',
		db='dbname'
	);
	cur = con.cursor()
	cur.execurte()
	cur.close()
	con.close()

class MyAPI( object ):
	def on_post( self, req, res, id ):
		if len(id) < 8:
			raise falcon.HTTPNotFound()
		buf = req.stream.read()
		data = json.loads( buf.decode('utf-8') )
		if not( "seq" in data and "stat" in data ):
			raise falcon.HTTPNotAccepted()
		cli = InfluxDBClient( host, port, user, password, dbname )
		ret = cli.query( "show measurements with measurement =\"{0}\";".format( id ) )
		tmp = []
		debugp = ""
		if len( ret.raw ) < 1:
			raise falcon.HTTPNotFound()
		if "log" in data:
			if "seq" in data["log"] and data["log"]["seq"] != 0:
				ret = cli.query( "select last(*) from \"{0}\";".format( id ), epoch="s" ) #Get last timestamp
				print( list( ret ) )
				if len( ret.raw ) > 0:
					lasttime = int(ret.raw[0]["time"])
					for i in range(data["log"]["seq"]):
						lasttime += 60
						tmp.append( {"measurement":id, "tags":{}, "time":lasttime*1000000000, "fields":{"Stat":"NC"}} )
		now = int(time.time())
		lasttime = now-60
		for i in range( data["seq"] ):
			tmp.append( {"measurement":id, "tags":{},"time":lasttime*1000000000, "fields":{"Stat":"NC"}} )
			lasttime -= 60
		tmp.append( {"measurement":id, "tags":{}, "time":now*1000000000, "fields":{"Stat":"OK"}} )
		cli.write_points( tmp )
		#check command
		ret=cli.query( "select value from \"{0}\" where type = 'command';".format( id ) )
		if len( ret.raw ) > 0:
			com = ret.raw[0]["value"]
			cli.query( "delete from \"{0}\" where type = 'command';".format(id) )
		else:
			com = ""
		res.status = falcon.HTTP_200
		res.body = str( {"stat":"OK", "time":now, "command":com, "debug":debugp } )
		res.content_type= "application/json"
app = falcon.API()
app.add_route( '/{id}', MyAPI() )


