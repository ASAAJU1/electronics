"""
CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

import as module. just quick common functions between scrtips. 
"""


def sleepTest():
    """Quick way to goto sleep"""
    #wakeupOn(GPIO_10, True, False)
    sleep(0,0)
    
def zQuickSleepTest(Minute,Second):
    eventString = "Going to sleep, wake at: " + str(Minute) + ":" + str(Second)
    rpc(portalAddr, "logEvent", eventString)
    writeClockAlarm(Minute,Second)
    sleep(0,0)
    
def zCalcWakeTime10():
    """Set the RTC INT to triger at the next 10 minute interval"""
    # This is an abbreviated part of displayClockTime retrieving
    # only the current seconds and minutes.
    buff = readPCF2129(0x03,2)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    
    Minutes += 10
    Minutes = Minutes / 10
    Minutes = Minutes * 10
    if (Minutes > 50):
        Minutes = 0
    Seconds = 0
    writeClockAlarm(Minutes, 0)
    eventString = "Going to sleep, wake at: " + str(Minutes) + ":" + str(Seconds)
    rpc(portalAddr, "logEvent", eventString)
    writeClockAlarm(Minutes, 0)
    rpc(portalAddr, "WakeAlert", Minutes, Seconds)
    return str(Minutes)

def zCalcWakeTime1():
    """Set the RTC INT to triger in one minute, then goto sleep"""
    # This is an abbreviated part of displayClockTime retrieving
    # only the current seconds and minutes.
    buff = readPCF2129(0x03,2)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    
    Minutes += 1
    #Minutes = Minutes / 10
    #Minutes = Minutes * 10
    if (Minutes > 59):
        Minutes = 0
    writeClockAlarm(Minutes, Seconds)
    eventString = "Going to sleep, wake at: " + str(Minutes) + ":" + str(Seconds)
    rpc(portalAddr, "logEvent", eventString)
    writeClockAlarm(Minutes, Seconds)
    rpc(portalAddr, "WakeAlert", Minutes, Seconds)
    return eventString

def zCalcWakeTime5():
    """Set the RTC INT to triger in five minute, then goto sleep"""
    # This is an abbreviated part of displayClockTime retrieving
    # only the current seconds and minutes.
    buff = readPCF2129(0x03,2)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    
    Minutes += 5
    #Minutes = Minutes / 10
    #Minutes = Minutes * 10
    if (Minutes > 59):
        #Minutes = 0
        Minutes = Minutes - 60
    writeClockAlarm(Minutes, Seconds)
    eventString = "Going to sleep, wake at: " + str(Minutes) + ":" + str(Seconds)
    rpc(portalAddr, "logEvent", eventString)
    
    writeClockAlarm(Minutes, Seconds)
    return eventString

def zCalcWakeTime10info():
    """Set the RTC INT to triger at the next 10 minute interval"""
    # This is an abbreviated part of displayClockTime retrieving
    # only the current seconds and minutes.
    buff = readPCF2129(0x03,7)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    Hours = bcdToDec(ord(buff[2]) & 0x3F)
    Days = bcdToDec(ord(buff[3]) & 0x3F)
    DOW = bcdToDec(ord(buff[4]) & 0x07)
    Months = bcdToDec(ord(buff[5]) & 0x1F)
    Years = bcdToDec(ord(buff[6]))
    
    Minutes += 10
    Minutes = Minutes / 10
    Minutes = Minutes * 10
    if (Minutes > 50):
        Minutes = 0
        Hours += 1
    if (Hours > 23):
        Hours = 0
        Days += 1
        DOW += 1
    Seconds = 0
    writeClockAlarm(Minutes, Seconds)
    eventString = "Going to sleep, wake at: " + str(Hours) + ":" + str(Minutes) + ":" + str(Seconds)
    rpc(portalAddr, "logEvent", eventString)
    writeClockAlarm(Minutes, Seconds)
    rpc(portalAddr, "WakeDisplay", Years,Months,Days,DOW,Hours,Minutes,Seconds)
    return str(Minutes)