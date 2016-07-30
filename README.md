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

