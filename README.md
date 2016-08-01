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

[Cmd]
Test : python,test.py,-t,hello world


```

#### Then:
```
python zeroph.py -n Test

```

##### You can add new cmd in [Cmd] section at will and then call them in threads with a word
Then the cmd can be adjusted at will without having to go over the whole code and also lunch separate process in threads

### TODOS: 

- Add a json-rpc server listening, start as default init cmds
- Make ini commands in config and start them at init with chosen delays
- make group command that can be launch toheter as init
- ad websocket server listening and start it at defauult init
- Find a way to send rcv other type of dasta than string
- design the follower class that will listen to PID of threads (and ensure PID is passed thourgth the process pipeline)
- make a optional middleware strategy(python class instance) that will trigger pass assertion on return value before sending it back,(will be appended for mandatory strategies)
- make a global onSuCess, onFail, onError, onDisconnect, onConnRefused subclass make it in a template python call to be easily customizable
- Make unittests
- Make readable documentation


