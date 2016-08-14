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
import traceback
import sys
import os

# load configs
Config = ConfigParser.ConfigParser()
Config.read("config.ini")
section = Config.sections()
_HOST=Config.get("Default",'Host')
_PORT=Config.get("Default",'Port')
_INIT= []
for (each_key, each_val) in Config.items("Init"):
    _INIT.append([ each_key, each_val])

class ZeroPh(object):
    def __init__(self, verbose):
        self.verbose = verbose
        self.host=_HOST
        self.port=_PORT
        self.handler = ZeroPhHandler(self.verbose)
        self.server = ZeroPhServer(self.verbose, self.host, self.port)
        self.client = ZeroPhClient(self.verbose, self.host, self.port)

                
class ZeroPhServer(ZeroPh):    
    def __init__(self, verbose, host, port):
        
        self.verbose= verbose
        # server
        self.context= zmq.Context()
        self.socket= self.context.socket(zmq.REP)
        self.processes= int(Config.get("Default", "processes"))
        self.host= host
        self.port= port
        self.client = ZeroPhClient(self.verbose, self.host, self.port)
        
    def req(self, msg):
        """
        Initiate the request and instantiate a new worker and start it
        
        @params: {msg} cmd msg for the worker
        @rtype: {str} launch res with result
        
        """
        worker = ZeroPhWorker(self.verbose, self.processes)
        q1 = self.enthread(worker.start_jobs, (msg, self.verbose))
        return self.res(str(q1.get()))
        
    def res(self, res):
        """
        Send the res result to the client 
        
        @params:{res} res results
        
        """
        # server
        self.socket.bind(self.host+':'+self.port)
        self.socket.send(str(res))
        return True
        
    def run_server(self):
        """
        Start the server. Listen for cmd call
        
        """
        # server
        self.socket.bind(self.host+':'+self.port)
        
        if self.verbose:
            print(str(timenow())+' ZeroPhServer() INFO | socket now listen on port: ' + str(self.port))
        self.init()
        while True:
            msg = self.socket.recv()
            if isinstance(msg, str):
                self.req(msg)
            else:
                print(str(timenow())+' ZeroPhServer() WARNING | Error: cmd was not a string ')
                
    def enthread(self, target, args):
        q = Queue.Queue()
        def wrapper():
            q.put(target(*args))
            q.task_done()
        t = threading.Thread(target=wrapper)
        try:
            t.start()
            response = q
            return response 
        except (KeyboardInterrupt, SystemExit):
            cleanup_stop_thread();
            sys.exit()
            
    def init(self):
        """
        Start the base services described in config.ini in [Init] section
        
        If nothing then continue on listening. 
        if key is a number then wait the number of seconds
        @params: {file} config.ini
        @rtype:{}
        
        """
        if len(_INIT) >0:
            self.client.parse_commands(_INIT)
        else:
            pass

class ZeroPhClient(ZeroPh):    
    def __init__(self, verbose, host, port):
        self.verbose= verbose
        # client
        self.context= zmq.Context()
        self.socket= self.context.socket(zmq.REQ)
        self.host= host
        self.port= port
        
    def req(self, cmd):
        """
        Send a cmd to the server 
        
        @params: {str} cmd: cmd to send

        """
        # client
        self.socket.connect(self.host+':'+self.port)
        if self.verbose:
            print(str(timenow())+' ZeroPhServer() INFO | cmd sent to server: ' + str(cmd))
        self.socket.send(cmd)
        return True
        
    def res(self):
        """
        Send response from the server to the handler, then return it back
        
        """
        # client 
        self.socket.connect(self.host+':'+self.port)
        msg = socket.recv()
        if self.verbose:
            print(str(timenow())+' ZeroPhServer() INFO | server returned response: ' + str(msg))
        res = self.handler.onReturn(msg, "")
        return res

    def send(self, _type, _file, _cmd):
        """
        Send a cmd to the request method
        
        @params: {str} _type: type of comand ex: python, node, sh
        @params: {str} _file: filename to be called
        @params: {str} _cmd: the actual cmd and args that will be apllied to the cmd
        @rtype: {} get the response form the server which should be stdout of the called process
        
        """
        cmd = s.join((_type,_file))
        for arg in _cmd:
            if arg != ",":
                cmd= cmd+","
                if self.verbose:
                    print(str(timenow())+' ZeroPhServer() INFO | arg in _cmd: ' + str(arg)) 

                cmd = cmd + arg.replace("[","").replace("]","") 
                
        self.req(cmd)

    def call(self, method):
        """
        Send a cmd to the server to be run in a thread
        
        @params: {str} _type: type of comand ex: python, node, sh
        @params: {str} _file: filename to be called
        @params: {str} _cmd: the actual cmd and args that will be apllied to the cmd
        @rtype: {} get the rsponse form the server which should be stdout of the called process
        
        """
        # client
        self.socket.connect(self.host+':'+self.port)
        
        try:
            cmd= Config.get("Cmd", method)
        except:
            print(str(timenow())+' ZeroPhServer() Warning | method does NOT exist in [Cmd] config.ini : ' + str(method))
            cmd=str(timenow())+' ZeroPhServer() Warning | method does NOT exist in [Cmd] config.ini : ' + str(method)
        if self.verbose:
            print(str(timenow())+' ZeroPhServer() INFO | cmd sent to server: ' + str(cmd))
            
        self.req(cmd)
    
    def wait_and_call(self, seconds, command):
        """
        wait number of seconds before lunching command
        @params:{int} number of seconds
        @params:{str} command
        @rtype{func} call the command
        
        """
        time.sleep(seconds)
        result = self.call(command)
        return result
    
    def call_group(self, group):
        """
        Add the possibility to manually (in in method group!) call a method group .
        
        @params: {str} section group to fetch from config
        @rtype: result
        
        """
        try:
            commands = self.parse_command_group(group)
            result= self.parse_commands(commands)
            return result
            
        except ValueError as (e):
            print(str(timenow())+' ZeroPhParser() WARNING | the group DOES NOT exists please try again: ' + str(msg)) 
            return e
              
    def parse_command_group(self, section):
        """
        Parse the group of command and store in into a list
        
        @params: {str} Section name to get list from
        @rtype: {list} List of key,value to be parsed as commands
        
        """
        result =[]
        for (each_key, each_val) in Config.items(section):
            result.append([ each_key, each_val])
        return result
        
    def parse_commands(self, commands):
        """
        Parse commands
        
        Will read the key and determine if it is a wait call or a cascade list
        (number can be contained in the list and will trigger a wait_and_call)
        
        @params:{list} list of commands (format: [[key,value],[key,value]] )
        
        """
        if len(commands) >0:
            for x in range(len(commands)):
                if self.verbose:
                    print(str(timenow())+' ZeroPhParser() INFO | parse_commands(): '+str(commands[x]))
                if is_number(commands[x][0]):
                    if self.verbose:
                        print(str(timenow())+' ZeroPhParser() INFO | parse_commands(): '+str(commands[x][1])+': waiting ' + str(commands[x][0])+' seconds')
                    self.wait_and_call(int(commands[x][0]), commands[x][1])

                    continue
                elif isinstance(commands[x][0], str):
                    self.call(int(commands[x][0]), commands[x][1])
        else:
            return self.handler.onError("ERROR in parse_commands: ", "commands was empty") 
        
class ZeroPhWorker(ZeroPh):    
    def __init__(self, verbose, processes):
        self.verbose =verbose
        self.processes = processes

    def start_jobs(self, msg, verbose):
        """
        """
        # Create a list of jobs and then iterate through
        # the number of processes appending each process to
        # the job list 
        out_q = Queue.Queue()
        jobs = []
        result = ""
        for i in range(0, self.processes):
            out_list = list()
            process = multiprocessing.Process(target=self.cmd, 
                                            args=(msg, self.verbose, out_q))
            jobs.append(process)
            process.start()
            result += out_q.get()

        # Ensure all of the processes have finished
        for j in jobs:
            j.join()
        
        if self.verbose:
            print(str(timenow())+' ZeroPhParser() INFO | Joblist List processing complete. | result: '+str(result))
        return result

    def cmd(self, cmd, verbose):
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
                
            out_q.put(stdout)

            
class ZeroPhHandler(ZeroPh):    
    def __init__(self, verbose):
        self.verbose =verbose

    def onError(self, error, message, _id):
        """
        onError return a print message with the stacktrace or message
        
        @params:{str} error
        @params: {str} message
        @params: {str} id for following (to be implemented)
        
        """
        if self.verbose:
            print(str(timenow())+' ZeroPhHandler() ERROR | server returned error: '+str(error)+' message: ' + str(message))  
        return True
    
    def onFail(self, error, message, _id):
        """
        onFail return a print message with the message of the fail but let the cascade coninue
        
        @params:{str} error
        @params: {str} message
        @params: {str} id for following (to be implemented)
        
        """
        if self.verbose:
            print(str(timenow())+' ZeroPhHandler() FAIL | server returned fialed return value: '+str(error)+' message: ' + str(message)) 
        _continue = Config.get("Default", "onFail")
        if _continue: 
            return True 
        else:
            return False
                

    def onReturn(self, value, _id):
        """
        onReturn value strategy
        Here will be run the strategy
        
        @params:{str} return value

        """
        # put the strategy
        if self.verbose:
            print(str(timenow())+' ZeroPhHandler() INFO | server returned return value: '+str(value)+' for: ' + str(_id)) 
        if value:
            return value
        else:
            return False
            
def timenow():
    return datetime.datetime.now().time()

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(description='zeromq server/client for CmdToThread()')
    parser.add_argument('-v', '--verbose', action='store_true', help='Flag to verbose')
    parser.add_argument('-t', '--_type', help='{string} type of file to be called, ex: python , node, sh, ./')
    parser.add_argument('-f', '--_file', help='{string} filename to be called, ex: example.py, do.sh, index.js')
    parser.add_argument('-c', '--cmd', nargs='+', help='{list} cmd args and parameters')
    parser.add_argument('-s', '--start', action='store_true', help='start the server')
    parser.add_argument('-n', '--name',  help='{string} Name of the method to fetch in config')
    parser.add_argument('-g', '--group',  help='{string} Call a method group')
    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True
    zeroph = ZeroPh(verbose)
    
    if args._type and args._file and args.cmd:
        zeroph.client.send(args._type, args._file, args.cmd)
    elif args.start:
        zeroph.server.run_server()
    elif args.name:
        result = zeroph.client.call(args.name)
    elif args.group:
        result= zeroph.client.call_group(args.group)
    else:
        print(str(timenow())+' ZeroPh() WARNING | missing argument, need a _type, _file and cmd, start the server with -s')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print 'Interrupted'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
