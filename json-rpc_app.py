#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author : Ian Bicking - Jean-Philippe Beaudet@s3r3nity

App handle zeroph via json-rpc endpoint

The json-rpc server will trigger zeroph methods, or group call. 
This is a alternative endpoint from command line call
Example smtp server instance command:

smtplib:SMTP('localhost')

Example cmd request json:

{"cmd": "cmdName",
 "id": "arbitrary-something"}
    
Example succes response: 
​
{"result": the_result,
 "error": null,
 "id": "arbitrary-something"}
 
Example error response:
 
 {"result": null,
 "error": {"name": "JSONRPCError",
           "code": (number 100-999),
           "message": "Some Error Occurred",
           "error": "whatever you want\n(a traceback?)"},
 "id": "arbitrary-something"}
 
"""

from webob import Request, Response
from webob import exc
from simplejson import loads, dumps
import traceback
import sys
import zeroph

class JsonRpcApp(object):
    """
    Serve the given object via json-rpc (http://json-rpc.org/)
    """

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            resp = self.process(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)

    def process(self, req):
        if not req.method == 'POST':
            raise exc.HTTPMethodNotAllowed(
                "Only POST allowed",
                allowed='POST')
        try:
            json = loads(req.body)
        except ValueError, e:
            raise ValueError('Bad JSON: %s' % e)
        try:
            method = json['cmd']
            #params = json['params']
            id = json['id']
        except KeyError, e:
            raise ValueError(
                "JSON body missing parameter: %s" % e)
        if method.startswith('_'):
            raise exc.HTTPForbidden(
                "Bad method name %s: must not start with _" % method)
                
        #if not isinstance(params, list):
            #raise ValueError(
                #"Bad params %r: must be a list" % params)
                
        # Fun start here
        ##############################################
        #try:
            #z = zeroph.ZeroPh(True)
            #method = z.call(method)
            #method = getattr(self.obj, method)
        #except AttributeError:
            #raise ValueError(
                #"No such cmd %s" % method)
        try:
            z = zeroph.ZeroPh(True)
            result = z.call(method)
            #result = method(*params)
        except:
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            error_value = dict(
                name='JSONRPCError',
                code=100,
                message=str(exc_value),
                error=text)
            return Response(
                status=500,
                content_type='application/json',
                body=dumps(dict(result=None,
                                error=error_value,
                                id=id)))
        return Response(
            content_type='application/json',
            body=dumps(dict(result=result,
                            error=None,
                            id=id)))
