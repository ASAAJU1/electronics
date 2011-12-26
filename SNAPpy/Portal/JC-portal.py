import time
#import os, sys, glob, shutil, time
#import winreg as winreg

rf_solar = "\x00\x65\x1D"

def dTime():
    #print time.localtime()
    Year = int(time.strftime('%y'))
    Month = int(time.strftime('%m'))
    Date = int(time.strftime('%d'))
    Hour = int(time.strftime('%H'))
    Minute = int(time.strftime('%M'))
    Second = int(time.strftime('%S'))
    DOW = int(time.strftime('%w'))
    
    print Year,Month,Date,Hour,Minute,Second,DOW
    #writeClockTime(Year,Month,Day,DOW,Hour,Minute,Second)
    rpc(rf_solar, "writeClockTime", Year, Month, Date, DOW, Hour, Minute, Second)
    
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