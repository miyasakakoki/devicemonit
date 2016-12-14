#!/usr/bin/python3

import falcon

class MyAPI( object ):
	def on_get( self, req, res ):
		res.status = falcon.HTTP_200
		res.body = 'test'
		res.content_type = 'text/plain'
	def on_post( self, req, res ):
		res.status = falcon.HTTP_200
		res.content_type = 'test/plain'
		res.body = 'post'
app = falcon.API()
app.add_route( '/', MyAPI() )


