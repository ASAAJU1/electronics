from __future__ import with_statement
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
#import serial
import apsw
#from p_clock_m import *
#from p_display_m import *
#from p_cnc_m import *

jccsv = 'C:/jc/jcCSV.txt'
jcsql = 'C:/jc/dc.sqlite3'
#import thermistor
import wx
import wx.grid
buttonCount = 0
frame = None
frame2 = None

CSV_FILENAME = "tempDataLog.csv"

def getPortal():
    rpc(remoteAddr, "addressPortal")
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
    print "logToSQL called from: " + name + "," + mac + ": " + loginfo
    con = sqlite3.connect(jcsql)
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO snapLogs (NodeMAC, name, loginfo) VALUES (?,?,?)", (mac, name, loginfo))

def getcmdSQL():
    mac = convertAddr(remoteAddr)
    print "getcmdSQL called from: " + mac + "."
    con = sqlite3.connect(jcsql)

    with con:
        cur = con.cursor()
        print "Running Select for " + mac + "...",
        cur.execute('SELECT * FROM RunMe WHERE NodeMAC=:NM and ACTIVE=1',{"NM": mac})
        print "Select done!"

        rows = cur.fetchall()

        for row in rows:
            linefields = str(row[2]).split(',')
            com.rpc(com.rpc_source_addr(), *linefields[0:])
            formattedTime = time.strftime("%Y-%m-%d %H:%M:%S")
            id = str(row[0])
            if (str(row[6]) == '0'):
                cur.execute('UPDATE RunMe SET dtRun=?,active=0 WHERE id=?', (formattedTime,id))
            else:
                cur.execute('UPDATE RunMe SET dtRun=? WHERE id=?', (formattedTime,id))

            eventString = str(row[0]) + " sent: " + str(row[2])
            cur.execute('INSERT INTO snapLogs (NodeMac, name, loginfo) VALUES (?,?,?)', (mac, mac, eventString))
            con.commit()
            print row[0]
            #subject = "Sent cmd to " + mac
            #body = "Sent " + str(linefields) + " to " + str(mac) + " at " + str(formattedTime)
            #sendAlert('jc@jcwoltz.com', subject, body)

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

def setRFTime(nodeAddr):
    """Call with nodeAddr to set the time on that node"""
    Year = int(time.strftime('%y'))
    Month = int(time.strftime('%m'))
    Date = int(time.strftime('%d'))
    Hour = int(time.strftime('%H'))
    Minute = int(time.strftime('%M'))
    Second = int(time.strftime('%S'))
    DOW = int(time.strftime('%w'))
    
    rpc(nodeAddr, "writeClockTime", Year, Month, Date, DOW, Hour, Minute, Second)
    eventString = str(displayDOW(DOW)) + " 20" + str(Year) + "." + str(Month) + "." + str(Date) + " " + str(Hour) + ":" +  str(Minute) + ":" + str(Second)
    remoteNode.setColumn("Clock set at", eventString)
    
def setRFPCF2129Time():
    """Call with nodeAddr to set the time on that node"""
    Year = int(time.strftime('%y'))
    Month = int(time.strftime('%m'))
    Date = int(time.strftime('%d'))
    Hour = int(time.strftime('%H'))
    Minute = int(time.strftime('%M'))
    Second = int(time.strftime('%S'))
    DOW = int(time.strftime('%w'))
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    #eventString = str(displayDOW(DOW)) + " 20" + str(Years) + "." + str(Months) + "." + str(Days) + " " + str(Hours) + ":" +  str(Minutes) + ":" + str(Seconds)
    print "mcastRpc Called at: " #+ eventString
    #mcastRpc(1, 3, "writeClockTime", Year, Month, Date, DOW, Hour, Minute, Second)

def displayDOW(DOW):
    if (DOW == 0):
        Day = "Sun"
    if (DOW == 1):
        Day = "Mon"
    if (DOW == 2):
        Day = "Tues"
    if (DOW == 3):
        Day = "Wed"
    if (DOW == 4):
        Day = "Thu"
    if (DOW == 5):
        Day = "Fri"
    if (DOW == 6):
        Day = "Sat"
    if (DOW == 7):
        Day = "Sun"
    #print Day
    return Day
def getcmd2x():
    """Called from node, pase file and rpc commands back to node"""
    f_cmds = open('C:/jc/jcCMDS.txt')
    #print "Called from: ",
    #print convertAddr(remoteAddr)
    #eventString = str(convertAddr(remoteAddr))
    for line in f_cmds.readlines():
        linefields = line.strip().split(',')
        if (linefields[0] == convertAddr(remoteAddr)):
            print linefields
            rpc(remoteAddr, *linefields[1:])
    f_cmds.close()
def dispayLastWriteAddress(tt):
    remoteNode.setColumn("Next EEPROM Address", tt)
    
def WakeAlert(Minutes, Seconds):
    eventString = str(Minutes) + " " + str(Seconds)
    remoteNode.setColumn("Wake At",eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def WakeDisplay(Years, Months, Days, DOW, Hours, Minutes, Seconds):
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    eventString = str(displayDOW(DOW)) + " " + str(20) + str(Years) + "." + str(Months) + "." + str(Days) + " " + str(Hours) + ":" +  str(Minutes) + ":" + str(Seconds)
    remoteNode.setColumn("Wake At",eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def GClockDisplay(Column, Years, Months, Days, DOW, Hours, Minutes, Seconds):
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    eventString = str(displayDOW(DOW)) + " " + str(20) + str(Years) + "." + str(Months) + "." + str(Days) + " " + str(Hours) + ":" +  str(Minutes) + ":" + str(Seconds)
    remoteNode.setColumn(Column,eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def LastReadDisplay(Years, Months, Days, DOW, Hours, Minutes, Seconds):
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    eventString = str(displayDOW(DOW)) + " " + str(20) + str(Years) + "." + str(Months) + "." + str(Days) + " " + str(Hours) + ":" +  str(Minutes) + ":" + str(Seconds)
    remoteNode.setColumn("LastRead At",eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def graph_generic(who, data):
    remoteNode.setColumn(who, data)
    logData(who, data)
    logToCSV(who, str(data))

def graph_generic_lqdts(who, data, lq, dts): 
    if who == None:
        who = convertAddr(remoteAddr)
    whoLQ = str(who) + "-LQ"
    logData(whoLQ,lq,128)
    logData(who, data)
    logToCSV(who, str(data))
    remoteNode.setColumn("Link", lq)
    remoteNode.setColumn("DT", dts)


def lm75aRawCalc(name, raw):
    """ Converts the raw reading from a LM75A Temp Sensor """
    if name == None:
        name = convertAddr(remoteAddr)
    intraw = int(raw)
    #print intraw.bit_length()
    intC = intraw >> 5
    #float fC 
    tC = intC / 8.0
    print tC
    tF = calcCtoF(tC)
    eventString = str(name) + "," + str(tF) + "," + str(tC)
    print eventString
    #logToCSV(name, eventString) 
    return tC

# Same as above, but logs to file
def loglm75aRawCalc(name, raw):
    """ Converts the raw reading from a LM75A Temp Sensor """
    mac = convertAddr(remoteAddr)
    if name == None:
        name = mac
    intraw = int(raw)
    intC = intraw >> 5
    tC = intC / 8.0
    tF = calcCtoF(tC)
    eventString = str(tC) + "," + str(tF) + "," + name
    #print eventString
    #formattedString = time.strftime("%m/%d/%Y %I:%M:%S %p") + "," + convertAddr(com.rpc_source_addr()) + "," + name + "," + eventString
    formattedString = time.strftime("%s") + "," + time.strftime("%m/%d/%Y %I:%M:%S %p") + "," + mac + "," + eventString
    print formattedString
    f = open('C:/jc/lm75alog.txt', 'a')
    f.write(formattedString + '\n')
    f.close()
    logData(name,tF,100)
    remoteNode.setColumn("Fahrenheit", tF)    
    return tC
##############################################################################
# intenal function to convert C to F
def calcCtoF(raw):
    fraw = float(raw)
    tempF = (fraw * 9)/5 + 32
    #print tempF
    return tempF
##############################################################################
def whereIsPortal(name, netid, scriptname):
    rpc(remoteAddr, 'setPortalAddr')
    