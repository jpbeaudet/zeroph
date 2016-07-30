#!/usr/bin/python
"""
Author : jean-Philippe Beaudet@s3r3nity

Dummy tester CLI

"""

import argparse
import datetime

class Testify(object):
    
    def __init__(self, verbose):
        self.verbose = verbose
    def go(self, sentence):
        print(str(timenow())+" | Testify() SUCCESS: sentence is: "+str(sentence))
        
def timenow():
    return datetime.datetime.now().time()
    
def main():
    parser = argparse.ArgumentParser(description='Twitterify cli')
    parser.add_argument('-v', '--verbose', action='store_true', help='Flag to verbose')
    parser.add_argument('-t', '--test', help='<string> test sentence')

    args = parser.parse_args()
    verbose = False
    if args.verbose:
        verbose = True
    if args.test:
        test = Testify(verbose)
        go = test.go(args.test)
    else:
        print(str(timenow())+" | Testify() WARNING: missing argument : write a dummy sentence to test if it prints ")

            
if __name__ == "__main__":
    main()

