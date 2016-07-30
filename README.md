# zeroph
Zero-ProcessHandler is a event driven process handler managing command line tool and/or executable files. It is built on zeromq for python, threading and subporcess


### Basic usage:

##### Start the server:

```
python cmd2thread.py -v -s

```

##### Launch a process :

```
python cmd2thread.py -v -t python -f test.py -c ["-t" , "hello world"]

```

### TODOS: 

- Built a handler that lunch and listen via zeromq command line tool
- Find a way to send rcv other type of dasta than string
- build a config file to easyly bind command to a namespace
- design the wrapper to launch via cmd2thread the bound command via name passing
- design the follower class that will listen to PID of threads (and ensure PID is passed thourgth the process pipeline)
- make a optional middleware strategy(python class instance) that will trigger pass assertion on return value before sending it back,(will be appended for mandatory strategies)
- make a global onFail, onError, onDisconnect, onConnRefused mandatory strategy for the handler
- make a command related .onFail, .onError, .onDisconnect, .onConnRefused strategy defaults
- Make custom error and update code with good error handling
- Make readable documentation


