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
import json

class CmdToThread(object):
    
    def __init__(self, verbose):
        self.verbose = verbose
        
    def run_server(self):
        """
        Start the server. Listen for cmd call
        
        """
        # server
        port = '5555'
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind('tcp://127.0.0.1:' + port)
        if self.verbose:
            print(str(timenow())+' CmdToThread() INFO | socket now listen on port: ' + str(port))
            
        while True:
            msg = socket.recv()
            if isinstance(msg, str):
                # Create two threads as follows
                try:
                    response = thread.start_new_thread(self.cmd, (msg))
                    socket.send(response)
                except:
                    print(str(timenow())+' CmdToThread() WARNING | Error: unable to start thread ')
                    socket.send(str(timenow())+' CmdToThread() WARNING | Error: unable to start thread ')
            else:
                print(str(timenow())+' CmdToThread() WARNING | Error: cmd was not converted to list ')
                
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
        socket.connect('tcp://127.0.0.1:5555')
        
        #cmd = sum([_type, _file], _cmd.split(" "))
        #cmd =[]
        #cmd.append(_type)
        #cmd.append(_file)
        s =" "
        cmd = s.join(("[",_type, _file))
        for arg in json.loads(_cmd):
            if self.verbose:
                print(str(timenow())+' CmdToThread() INFO | arg in _cmd: ' + str(arg))
            #cmd.append(arg)
            cmd = cmd + " " +arg
        cmd= cmd+ "]"
        #cmd = sum(cmd, _cmd)
        if self.verbose:
            print(str(timenow())+' CmdToThread() INFO | cmd sent to server: ' + str(cmd))
        #data = json.dumps(cmd)
        socket.send(cmd)
        msg = socket.recv()
        if self.verbose:
            print(str(timenow())+' CmdToThread() INFO | server returned response: ' + str(msg))
        
        
    def cmd(self, cmd):
        """
        Run the actual command in thread
        
        @params: {str} cmd: the command to run
        @rtype: {} return value
        
        """
        #query= json.loads(cmd)
        query= cmd.split(" ")
        if self.verbose:
            print(str(timenow())+' CmdToThread() INFO | Thread started for : ' + str(cmd))
        process = Popen(query, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            print(str(timenow())+' CmdToThread() WARNING | cmd returned error: ' + str(stderr))
        else:
            if self.verbose:
                print(str(timenow())+' CmdToThread() INFO | cmd returned stdout: ' + str(stdout))
            return stdout
            
def timenow():
    return datetime.datetime.now().time()
    
def main():
    parser = argparse.ArgumentParser(description='zeromq server/client for CmdToThread()')
    parser.add_argument('-v', '--verbose', action='store_true', help='Flag to verbose')
    parser.add_argument('-t', '--_type', help='{string} type of file to be called, ex: python , node, sh, ./')
    parser.add_argument('-f', '--_file', help='{string} filename to be called, ex: example.py, do.sh, index.js')
    parser.add_argument('-c', '--cmd', nargs='+', help='{list} cmd args and parameters')
    parser.add_argument('-s', '--start', action='store_true', help='start the server')
    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True
        
    cmd2thread = CmdToThread(verbose)
    
    if args._type and args._file and args.cmd:
        cmd2thread.send(args._type, args._file, args.cmd)
        print(str(timenow())+' CmdToThread() INFO | args.cmd: '+args.cmd)
    elif args.start:
        cmd2thread.run_server()
    else:
        print(str(timenow())+' CmdToThread() WARNING | missing argument, need a _type, _file and cmd, start the server with -s')

if __name__ == "__main__":
    main()
