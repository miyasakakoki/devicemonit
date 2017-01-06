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

#Query for Searching the Device ID from Database
q = "select sname from Devices where ID = {0};"


def existdevice( client, measurement ):
	ret = client.query( "show measurements with measurement = {0};".format(measurement) )
	return (len( ret.raw ) > 0)
def dbwrite( client, measurement, value, tag ):
	timestamp = int(time.time())*1000000000
	return client.write_points( [{"measurement":measurement,"tags":tag,"time":timestamp,"fields":{"value":value}}] )
	

class MyAPI( object ):
	def on_post( self, req, res, id ):
		if len(id) < 8:
			raise falcon.HTTPNotFound()
		data = json.loads( req.stream.read() )
		if not( "seq" in data and "stat" in data ):
			raise falcon.HTTPNotAccepted()
		cli = InfluxDBClient( host, port, user, password, dbname )
		ret = cli.query( "show measurements with measurement =\"{0}\";".format( id ) )
		tmp = []
		if len( ret.raw ) < 1:
			raise falcon.HTTPNotFound()
		if "log" in data:
			if "seq" in data["log"] and data["log"]["seq"] != 0:
				ret = cli.query( "select last(time) from \"{0}\";".format( id ) ) #Get last timestamp
				if len( ret.raw ) > 0:
					lasttime = int(ret.raw[0]["time"])
					for i in range(data["log"]["seq"]):
						lasttime += 60
						tmp.append( {"measurement":id, "tags":{}, "time":lasttime, "fields":{"value":"NC"}} )
		now = int(time.time())
		lasttime = now-60
		for i in range( data["seq"] ):
			tmp.append( {"measurement":id, "tags":{},"time":lasttime, "fields":{"value":"NC"}} )
			lasttime -= 60
		tmp.append( {"measurement":id, "tags":{}, "time":now, "fields":{"value":"OK"}} )
		cli.write_points( tmp )
		res.status = falcon.HTTP_200
		res.body = '{"stat":"OK", "time":{0} }'.format( now )
		res.content_type= "application/json"
app = falcon.API()
app.add_route( '/{id}', MyAPI() )


