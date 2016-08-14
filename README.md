# zeroph
Zero-ProcessHandler is a event driven process handler managing command line tool and/or executable files. It is built on zeromq for python, threading and subporcess


### Basic usage:

##### Start the server:

```
python zeroph.py.py -v -s

```

##### Launch a process :

```
python zeroph.py -v -t python -f test.py -c ["-t" , "hello world"]

```

#### config.ini
```
[Default]
Port: 5555
Host: tcp://127.0.0.1
processes: 3

[Cmd]
Test : python,test.py,-t,hello world

[TestGroup]
1: Test
2: Test
3: Test

```

#### Then -n + command name:
```
python zeroph.py -n Test

```
or
####  -g + groupcommand name:
The number in comandgroup config reprsent a waiting time before starting job list

```
python zeroph.py -n TestGoup

```

##### You can add new cmd in [Cmd] section at will and then call them in threads with a word
Then the cmd can be adjusted at will without having to go over the whole code and also lunch separate process in threads

#### You can call cmd you designed via json-rpc: simply call the command name. 

##### Start a smtp server (localhost :9999) 
Issue command line:
```
json-rpc_server.py smtplib:SMTP('localhost')

```

##### POST request to a single url (default : localhost:9999 )

##### Example command payload json:
```
{"cmd": "cmdName",
 "group" : false,
 "id": "arbitrary-something"}
 
```

##### or

```
{"cmd": "groupName",
 "group" : true,
 "id": "arbitrary-something"}
 
```
##### Example success response:
```
{"result": the_result,
 "error": null,
 "id": "arbitrary-something"}

```
##### Example error response:
```
 {"result": null,
 "error": {"name": "JSONRPCError",
           "code": (number 100-999),
           "message": "Some Error Occurred",
           "error": "whatever you want\n(a traceback?)"},
 "id": "arbitrary-something"}

```


### Dependencies:

- threading
- zeromq
- subprocess
- os
- arg-parse
- ConfigParser
- json-rpc
- webob
- traceback
- simplejson

### TODOS for v 1.0:

#### Priority 

- Make unittests
- switch from multithread to multiprocess(thinking about using joblibs maybe)
- makes jobs list into a queue self object with _id(pid) and trigger onReturn when a job are finished
- add a unsupervised process launching (not listening to return value) option

#### Secondary:

- design the follower class that will listen to PID of threads (and ensure PID is passed thourgth the process pipeline)
- add a stop process helper method using collected PID in the jobs queue
- make a optional middleware strategy(python class instance) that will trigger pass assertion on return value before sending it back,(will be appended for mandatory strategies)
- Make the helper class to encode return value to bytes then bytes2string sending types along and then convert it back to bytes and them to initial types(excluding string return value)
- Use traceback to collect error traceback from source cmd and retun it along the way to the user

#### Niceties:

- ad websocket server listening and start it at default init
- add a REST-ful endpoint with flask and/or django
- Make readable documentation

#### Bugs:
---- Fix the zmq with a option to trigget a non listenning thread ----
- Fix the the fact that it cannot call itself 


