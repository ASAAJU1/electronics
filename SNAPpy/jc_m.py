def sleepTest():
    """Quick way to goto sleep"""
    #wakeupOn(GPIO_10, True, False)
    sleep(0,0)
    
def zQuickSleepTest(Minute,Second):
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
    writeClockAlarm(Minutes, 0)
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
    return eventString

