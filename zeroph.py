#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author : Jean-Philippe Beaudet@s3r3nity

Server to run python command in threads

Wrapper to start any new comand in python threads
​
"""

import argparse
import zmq
import thread
import time
import datetime
import subprocess
from subprocess import Popen, PIPE
import threading
import Queue
import ConfigParser

# load configs
Config = ConfigParser.ConfigParser()
Config.read("config.ini")
section = Config.sections()
_HOST=Config.get("Default",'Host')
_PORT=Config.get("Default",'Port')


class ZeroPh(object):
    
    def __init__(self, verbose):
        self.verbose = verbose
        self.host=_HOST
        self.port=_PORT
        
    def run_server(self):
        """
        Start the server. Listen for cmd call
        
        """
        # server
        context = zmq.Context()
        socket = context.socket(zmq.REP)

        socket.bind(self.host+':'+self.port)
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | socket now listen on port: ' + str(self.port))
            
        while True:
            msg = socket.recv()
            if isinstance(msg, str):
                # Create two threads as follows
                q1 = enthread(cmd, (msg, self.verbose))
                socket.send(str(q1.get()))
            else:
                print(str(timenow())+' ZeroPh() WARNING | Error: cmd was not converted to list ')
                
    def send(self, _type, _file, _cmd):
        """
        Send a cmd to the server to be run in a thread
        
        @params: {str} _type: type of comand ex: python, node, sh
        @params: {str} _file: filename to be called
        @params: {str} _cmd: the actual cmd and args that will be apllied to the cmd
        @rtype: {} get the rsponse form the server which should be stdout of the called process
        
        """

        # client
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.host+':'+self.port)
        
        s =","
        cmd = s.join((_type,_file))
        for arg in _cmd:
            if arg != ",":
                cmd= cmd+","
                if self.verbose:
                    print(str(timenow())+' ZeroPh() INFO | arg in _cmd: ' + str(arg)) 

                cmd = cmd + arg.replace("[","").replace("]","") 

        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | cmd sent to server: ' + str(cmd))
        socket.send(cmd)
        msg = socket.recv()
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | server returned response: ' + str(msg))
            
    def call(self, method):
        """
        Send a cmd to the server to be run in a thread
        
        @params: {str} _type: type of comand ex: python, node, sh
        @params: {str} _file: filename to be called
        @params: {str} _cmd: the actual cmd and args that will be apllied to the cmd
        @rtype: {} get the rsponse form the server which should be stdout of the called process
        
        """
        # client
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.host+':'+self.port)
        try:
            cmd= Config.get("Cmd", method)
        except:
            print(str(timenow())+' ZeroPh() Warning | method does NOT exist in [Cmd] config.ini : ' + str(method))
            cmd=str(timenow())+' ZeroPh() Warning | method does NOT exist in [Cmd] config.ini : ' + str(method)
        if self.verbose:
            print(str(timenow())+' v() INFO | cmd sent to server: ' + str(cmd))
        socket.send(cmd)
        msg = socket.recv()
        if self.verbose:
            print(str(timenow())+' ZeroPh() INFO | server returned response: ' + str(msg))        
        
def cmd(cmd, verbose):
    """
    Run the actual command in thread
        
    @params: {str} cmd: the command to run
    @rtype: {} return value
        
    """

    if verbose:
        print(str(timenow())+' ZeroPh() INFO | Thread started for : ' + str(cmd))
    query= cmd.split(",")
    if verbose:
        print(str(timenow())+' ZeroPh) INFO | query : ' + str(query))
    process = Popen(query, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(str(timenow())+' ZeroPh() WARNING | cmd returned error: ' + str(stderr))
    else:
        if verbose:
            print(str(timenow())+' ZeroPh() INFO | cmd returned stdout: ' + str(stdout))
        return stdout
        
        
def enthread(target, args):
    q = Queue.Queue()
    def wrapper():
        q.put(target(*args))
    t = threading.Thread(target=wrapper)
    t.start()
    return q

def timenow():
    return datetime.datetime.now().time()
    
def main():
    parser = argparse.ArgumentParser(description='zeromq server/client for CmdToThread()')
    parser.add_argument('-v', '--verbose', action='store_true', help='Flag to verbose')
    parser.add_argument('-t', '--_type', help='{string} type of file to be called, ex: python , node, sh, ./')
    parser.add_argument('-f', '--_file', help='{string} filename to be called, ex: example.py, do.sh, index.js')
    parser.add_argument('-c', '--cmd', nargs='+', help='{list} cmd args and parameters')
    parser.add_argument('-s', '--start', action='store_true', help='start the server')
    parser.add_argument('-n', '--name',  help='{string} Name of the method to fetch in config')
    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True
    zeroph = ZeroPh(verbose)
    
    if args._type and args._file and args.cmd:
        zeroph.send(args._type, args._file, args.cmd)
    elif args.start:
        zeroph.run_server()
    elif args.name:
        zeroph.call(args.name)
    else:
        print(str(timenow())+' ZeroPh() WARNING | missing argument, need a _type, _file and cmd, start the server with -s')

if __name__ == "__main__":
    main()