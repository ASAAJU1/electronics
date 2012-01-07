import logging, logging.handlers, datetime, time, codecs, os, math, sys
import binascii
import time
import sys

def getcmd2x():
    """Called from node, pase file and rpc commands back to node"""
    f_cmds = open('C:/jc/jcCMDS.txt')
    #eventString = str(convertAddr(remoteAddr))
    for line in f_cmds.readlines():
        linefields = line.strip().split(',')
        if (linefields[0] == convertAddr(remoteAddr)):
            print linefields
            rpc(remoteAddr, *linefields[1:])
    f_cmds.close()
