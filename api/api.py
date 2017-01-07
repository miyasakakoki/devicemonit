#!/usr/bin/python3

import falcon
from influxdb import InfluxDBClient
import time
import json

host='localhost'
port=8086
user='test'
password='mytestuser'
dbname='devicemonit'

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
				ret = list(cli.query( "select last(Stat) from \"{0}\" where type <> 'command';".format( id ), epoch="s" ))[0] #Get last timestamp
				if len( ret ) > 0:
					lasttime = int(ret[0]["time"])
					for i in range(data["log"]["seq"]):
						lasttime += 60
						tmp.append( {"measurement":id, "tags":{}, "time":lasttime*1000000000, "fields":{"Stat":"NC"}} )
		now = int(time.time())
		lasttime = now-60
		for i in range( data["seq"] ):
			tmp.append( {"measurement":id, "tags":{},"time":lasttime*1000000000, "fields":{"Stat":"NC"}} )
			lasttime -= 60
		tmp.append( {"measurement":id, "tags":{}, "time":now*1000000000, "fields":{"Stat":"OK"}} )
		#check command
		ret=list(cli.query( "select last(Stat) from \"{0}\";".format( id ) ))[0][0]
		if ret["last"] == "OK" or ret["last"] == "NC":
			com = ""
		else:
			com = ret["last"]
		cli.write_points( tmp )
		res.status = falcon.HTTP_200
		res.body = str( {"stat":"OK", "time":now, "command":com, "debug":debugp } )
		res.content_type= "application/json"
app = falcon.API()
app.add_route( '/{id}', MyAPI() )


