from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *
from ds2764_ss import *
from pcf2129a_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<

CHG_ERROR = GPIO_9
CHG_STATUS = GPIO_10
RTC_INT = GPIO_2


isChargingPreviousState = False
chgStatusBlinkTimer = 0
chgStatusBlinkCounter = 0
secondCounter = 0

""" 
valid options for this are 
N - Not charging 
C - Charging 
D - Done Charging
- - unknown
"""
chargeStatus = '-'

noChgError = False

@setHook(HOOK_STARTUP)
def start(): 
    # I2C GPIO_17/18 used for MCP3424
    i2cInit(True)   
    global noChgError, chgStatusBlinkTimer, isChargingPreviousState
    setPinDir(CHG_ERROR, False)
    setPinDir(CHG_STATUS, False)
    monitorPin(CHG_ERROR, True)
    monitorPin(CHG_STATUS, True)
    
    setPinDir(RTC_INT, False)   #Input
    setPinPullup(RTC_INT, True) #Turn on pullup
    monitorPin(RTC_INT, True)   #monitor changes to this pin. Will go low on int
    wakeupOn(RTC_INT, True, False)  #Wake from sleep when pin goes low
    
    noChgError = readPin(CHG_ERROR)
    isChargingPreviousState = readPin(CHG_STATUS)
    
    # Go ahead and redirect STDOUT to Portal now
    #ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    #crossConnect(DS_STDIO,DS_TRANSPARENT)
    getPortalTime()
    initUart(0,9600)
    flowControl(0,False)
    crossConnect(DS_STDIO, DS_UART0)
        
    
    
    #Check if rtc has invalid yer, if so, automatically update rtc from portal
    checkClockYear()
    
    chgStatusBlinkTimer = getMs()
    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global secondCounter
    #DS2764FetchBasic()
    secondCounter += 1
    if secondCounter >= 30:
        DS2764FetchBasic()
        doEverySecond()      
        secondCounter = 0

def doEverySecond():
    #DS2764FetchBasic()
    cur = getDSCurrent()
    if (cur < 0):
        cur *= -1
    #rpc(portalAddr, "logData", "Lipo voltage mV", getDSVoltage(), 4500)
    #rpc(portalAddr, "logData", "Current draw mA", cur, 400)    
    #rpc(portalAddr, "logData", "Bat remain power", getDSACurrent(), 1000)
    ddt = displayClockDT()
    eventString = ddt + "," + str(getDSVoltage()) + "," + str(getDSCurrent()) + "," + str(getDSACurrent())
    print eventString
    rpc(portalAddr, "plotlq", loadNvParam(8), getLq())
    rpc(portalAddr, "infoDT", ddt)
    #print "Lipo mV -> " + str(getDSVoltage()) + "mV"
    #print "Lipo mA -> " + str(getDSCurrent()) + "mA"
    #print "Lipo mAh -> " + str(getDSACurrent()) + "mAh"    
    #print "Charging -> " + str(readPin(CHG_STATUS))
    #print "Charging error " + str(chg_error)
    
    
@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    """Hooked into the HOOK_GPIN event"""
    #mostly debug and pointless irw
    print str(pinNum),
    print str(isSet)
    eventString = "HOOK_GPIN " + str(pinNum) + str(isSet)
    rpc(portalAddr, "logEvent", eventString)
    
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
    eventString = "Going to sleep, wake at: " + str(Minutes) + ":" + str(Seconds)
    rpc(portalAddr, "logEvent", eventString)
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
    writeClockAlarm(Minutes, Seconds)
    return eventString

