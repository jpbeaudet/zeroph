#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author : 
author: Ian Bicking - Jean-Philippe Beaudet@s3r3nity

App handle zeroph via json-rpc endpoint

This will create the server on default port 9999

"""

import sys

def main(args=None):
    import optparse
    from wsgiref import simple_server
    parser = optparse.OptionParser(
        usage="%prog [OPTIONS] MODULE:EXPRESSION")
    parser.add_option(
        '-p', '--port', default='9999',
        help='Port to serve on (default 9999)')
    parser.add_option(
        '-H', '--host', default='127.0.0.1',
        help='Host to serve on (default localhost; 0.0.0.0 to make public)')
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args()
    if not args or len(args) > 1:
        print 'You must give a single object reference'
        parser.print_help()
        sys.exit(2)
    app = make_app(args[0])
    server = simple_server.make_server(
        options.host, int(options.port),
        app)
    print 'Serving on http://%s:%s' % (options.host, options.port)
    server.serve_forever()
    
def make_app(expr):
    module, expression = expr.split(':', 1)
    __import__(module)
    module = sys.modules[module]
    obj = eval(expression, module.__dict__)
    return JsonRpcApp(obj)
    
if __name__ == '__main__':
    main()
