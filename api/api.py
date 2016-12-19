#!/usr/bin/python3

import falcon
from influxdb import InfluxDBClient
import time

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
	timestamp = time.time()
	return client.write_points( [{"measurement":measurement,"tags":tag,"time":timestamp,"fields":{"value":value}}] )
	

class MyAPI( object ):
	def on_get( self, req, res, id ):
		#Connect to Database
		cli = InfluxDBClient( host, port, user, password, dbname )
		if not existdevice( cli, id ):
			raise falcon.HTTPNotFound()
		if not dbwrite( cli, id, 1, {"stat":"up"} ):
			print("miss1")
		res.status = falcon.HTTP_200
		res.body = '{"stat":"ok"}'
		res.content_type = 'application/javascript'
	
	def on_post( self, req, res, id ):
		cli = InfluxDBClient( host, port, user, password, dbname )
		if not existdevice( cli, id ):
			raise falcon.HTTPNotFound()
		if not dbwrite( cli, id, 1, {} ):
			print("miss2")
		res.status = falcon.HTTP_200
		res.content_type = 'application/javascript'
		res.body = '{"stat":"ok"}'


app = falcon.API()
app.add_route( '/{id}', MyAPI() )


