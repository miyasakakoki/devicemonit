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
	def on_get( self, req, res, id ):
		json = json.loads( req.stream.read().decode('utf-8') )
		tmp = dbwrite( json, id, "UP" )
		res.status = falcon.HTTP_200
		res.content_type = "application/json"
		if tmp == "notfound":
			raise falcon.HTTPNotFound()
		elif tmp == "notcceptable":
			raise falcon.HTTPNotAcceptable()
		else:
			res.body = "{ \"stat\":\"OK\", \"time\": \"{0}\" }".format( int(time.time()) )
	def on_post( self, req, res, id ):
		json = json.loads( req.stream.read().decode('utf-8') )
		tmp = dbwrite( json, id, "OK" )
		res.status = falcon.HTTP_200
		res.content_type = "application/json"
		if tmo == "notfound":
			raise falcon.HTTPNotFound()
		elif tmp == "notacceptable":
			raise falcon.HTTPNotAcceptable()
		else:
			res.body = "{ \"stat\":\"OK\", \"time\": \"{0}\" }".format( int(time.time()) )
	def dbwrite( json, id, meth ):
		cli = InfluxDBClient( host, port, user, password, dbname )
		ret = cli.query( "show measurements with measurement = {0};".format(id) )
		if len(ret.raw) < 1:
			return "notfound"
		if "seq" not in json or "data" not in json:
			return "notacceptable"
		if len(json["data"]) == 0:
			cli.write_points( [{"measurement":id, "tags":{}, "time":(int(time.time())*1000000000), "fields":{"stat": (meth=="GET"?"UP":"OK")} }] )
		else:
			if "lasttime" not in json:
				return "ntoacceptable"
			tmpdat = []
			buf = []
			flag == True
			for item in json["data"]:
				if item["stat"] == "UP":
					flag = False
					buf = []
				else:
					if flag:
						tmpdat.append( item )
					else:
						buf.append( item )
			if len( buf ) > 0:
				tmpdat += buf
				tmptime = int(time.time())-len( buf )*60
			lasttime = int(json["lasttime"])
			buf = []
			for item in tmpdat:
				if "seq" not in item or "stat" not in item:
					return "notacceptable"
				if item["stat"] == "UP":
					lasttime = tmptime
					buf.append( { "measurement":id, "tags":{"seq":item["seq"]}, "time":lasttime*1000000000, "fields":{"stat":"UP"} } )
				elif item["stat"] == "NC":
					lasttime += 60
					buf.append( { "measurement":id, "tags":{}, "time":(lasttime*1000000000), "fields":{"stat":"NC"} } )
			buf.append( { "measurement":id, "tags":{}, "time":(int(time.time())*1000000000), "fields":{"stat": (meth=="GET"?"UP":"OK")} } )
			cli.write_points( tmp )
		return True
	
app = falcon.API()
app.add_route( '/{id}', MyAPI() )


