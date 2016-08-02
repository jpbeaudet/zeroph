#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author : Jean-Philippe Beaudet@s3r3nity

Server to test zmq with zeroph
​
"""

import argparse
import zmq
import time
import datetime



class TestZmq(object):
    
    def __init__(self, verbose):
        self.verbose = verbose
        self.host="tcp://127.0.0.1"
        self.port='5557'
        
    def run_server(self):
        """
        Start the server. Listen for test call
        
        """
        # server
        context = zmq.Context() 
        socket = context.socket(zmq.REP)

        socket.bind(self.host+':'+self.port)
        if self.verbose:
            print(str(timenow())+' TestZmq() INFO | socket now listen on port: ' + str(self.port))
            
        while True:
            msg = socket.recv()
            if isinstance(msg, str):
                socket.send(msg)
            else:
                print(str(timenow())+' TestZmq() WARNING | Error: cmd was not a string ')
                
    def send(self, sentence):
        """
        Send a test sentence to the server and expect it to be returned

        """

        # client
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.host+':'+self.port)
        
        if self.verbose:
            print(str(timenow())+' TestZmq() INFO | msg sent to server: ' + str(sentence))
        socket.send(sentence)
        msg = socket.recv()
        if self.verbose:
            print(str(timenow())+' TestZmq() INFO | server returned response: ' + str(msg))

def timenow():
    return datetime.datetime.now().time()
    
def main():
    parser = argparse.ArgumentParser(description='zeromq test server/client')
    parser.add_argument('-v', '--verbose', action='store_true', help='Flag to verbose')
    parser.add_argument('-t', '--test', help='{string} sentence to test with')
    parser.add_argument('-s', '--start', action='store_true', help='start the server')
    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True
    testzmq = TestZmq(verbose)
    
    if args.test:
        testzmq.send(args.test)
    elif args.start:
        testzmq.run_server()
    else:
        print(str(timenow())+' TestZmq() WARNING | missing argument, need a sentence or start the server with -s')

if __name__ == "__main__":
    main()

