"""
J.C. Woltz's Portal Script. 
"""
"""
    logSupport.py - one method of supporting "log to file" functionality

    Makes use of the standard logging capabilities of Python
"""

import logging, logging.handlers, datetime, time, codecs, os, math, sys
import binascii
import time
import sys
sys.path.append('C:\Python25\Lib\site-packages')
sys.path.append('C:\Python25\Lib\site-packages\serial')
print sys.path
import serial
import apsw
from p_clock_m import *
from p_display_m import *
from p_cnc_m import *

jccsv = 'C:/jc/jcCSV.txt'
jcsql = 'C:/jc/downloads/software/sqlite/snapconnect.sqlite3'
#import thermistor
import wx
import wx.grid
buttonCount = 0
frame = None
frame2 = None

CSV_FILENAME = "tempDataLog.csv"

def getPortal():
    rpc(remoteAddr, "addressPortal", Portal.netAddr)
    eventString = "getPortal called from: " + convertAddr(remoteAddr) + ". Replied with: " + convertAddr(Portal.netAddr)
    print eventString

def pingESCO():
    rpc("\x00\x31\x56", "vmStat", 10)

def convertTMP36200(adc):
    #print adc,
    miiil = (adc) * (1600.0000/1024.0000)
    #print miiil
    tempc = (miiil - 500) / 10
    print tempc
    convertTMP36200f(tempc)
    #return tempc
def convertTMP36200f(val):
    tempf = val * 1.8 + 32
    print tempf
    return tempf


###############################################################################
## Various Test function to help people on forums #############################
###############################################################################
###############################################################################

def printValue(value):
    print value
###############################################################################
## Below is from Synapse Wireless    ##########################################
## Some are modified  #########################################################
###############################################################################
def plotlq(who, lq, dts): 
    logData(who,lq,128)
    remoteNode.setColumn("Link", lq)
    remoteNode.setColumn("DT", dts)

def infoDT(dts):
    remoteNode.setColumn("DT", dts)
    
def infoLQ(who, lq):
    remoteNote.SetColumn("Link", dts)
    

def get_portal_logger():
    rpc(remoteAddr, "set_portal_addr", Portal.netAddr)

def adc_to_resistance(adc_val):
    return PULLUP_RESISTOR * adc_val / (ADC_FULLSCALE - adc_val)

###############################################################################
## Various Test function to help people on forums #############################
###############################################################################
###############################################################################

def logToCSVEEPROM(name, logInfo):
    """Logs to CSV witth node name and loginfo as sting. Strips the EOB from the end"""
    if name == None:
        name = convertAddr(remoteAddr)
    #formattedadcValue = strftime("%m/%d/%Y %I:%M:%S %p") + "," + name + "," + "%.2f" % batt + "," + signal
    toLog = logInfo.split(',EOB')
    formattedString = time.strftime("%m/%d/%Y %I:%M:%S %p") + "," + name + "," + toLog[0]
    print formattedString
    f = open(jccsv, 'a')
    f.write(formattedString + '\n')
    f.close()
    #rpc(remoteAddr, "tACKl", 1)

def logToCSV(name, logInfo):
    if name == None:
        name = convertAddr(remoteAddr)
    #formattedadcValue = strftime("%m/%d/%Y %I:%M:%S %p") + "," + name + "," + "%.2f" % batt + "," + signal
    #toLog = logInfo.split(',EOB')
    #formattedString = time.strftime("%m/%d/%Y %I:%M:%S %p") + "," + name + "," + toLog[0]
    formattedString = time.strftime("%m/%d/%Y %I:%M:%S %p") + "," + convertAddr(remoteAddr) + "," + name + "," + logInfo
    print formattedString
    f = open(jccsv, 'a')
    f.write(formattedString + '\n')
    f.close()
    #rpc(remoteAddr, "tACKl", 1)

def convertAddr(addr):
    """Converts binary address string to a more readable hex-ASCII address string"""
    return binascii.hexlify(addr)

##############################################################################
# Unfinished to log to SQLite3
def logToSQL(name, loginfo):
    mac = convertAddr(remoteAddr)
    con = sqlite3.connect(jcsql)
    eventSting = "logToSQL: " + mac + ", " + name + ", " + loginfo
    print eventSting
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM RunMe WHERE mac=:mac and active = 'True'",{"mac": mac})
        con.commit()

        rows = cur.fetchall()
        for row in rows:
            linefields = row[0].strip().split(',')
            print linefields
            com.rpc(remoteAddr, *linefields[1:])
            print row[0]
    except sqlite3.OperationalError, msg:
        print msg
        
    #con = sqlite3.connect('/root/dc.sqlite')
    try:
        #cur = con.cursor()
        cur.execute("INSERT INTO snapLogs (mac, name, loginfo) VALUES (?,?,?)", (mac, name, loginfo))
        con.commit()
    except sqlite3.OperationalError, msg:
        print msg
    

def printAPSWinfo():
    print "      Using APSW file",apsw.__file__                # from the extension module
    print "         APSW version",apsw.apswversion()           # from the extension module
    print "   SQLite lib version",apsw.sqlitelibversion()      # from the sqlite library code
    print "SQLite header version",apsw.SQLITE_VERSION_NUMBER   # from the sqlite header file at compile time
def createADB():
    connection=apsw.Connection("dbfile")
    cursor=connection.cursor()
    cursor.execute("CREATE TABLE RunIT(id INTEGER PRIMARY KEY AUTOINCREMENT, NodeMAC TEXT, cmd2x TEXT, addDate DATETIME)")
    cursor.execute("BEGIN  UPDATE RunIT SET addDate = DATETIME('NOW')  WHERE rowid = new.rowid; END;")
    cursor.execute("CREATE TABLE snapLogs(Id INTEGER PRIMARY KEY AUTOINCREMENT, NodeMAC TEXT, name TEXT, loginfo TEXT, addDate DATETIME)")
    