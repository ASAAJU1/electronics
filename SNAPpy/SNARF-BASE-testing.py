from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *
from pcf2129a_m import *
from lm75a_m import *
from m24lc256_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
secondCounter = 0 
minuteCounter = 0
datablock = 1
taddress = 64

VAUX = GPIO_5
RTC_INT = GPIO_10


@setHook(HOOK_STARTUP)
def start():    
    setPinDir(VAUX, True)
    writePin(VAUX, False)
    setPinDir(RTC_INT, False)
    setPinPullup(RTC_INT, True)
    monitorPin(RTC_INT, True)
    wakeupOn(RTC_INT, True, False)
    
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    initUart(0,9600)
    flowControl(0,False)
    crossConnect(DS_STDIO,DS_UART0)
        
    # I2C GPIO_17/18 rf100. rf200 needs external pullups.
    i2cInit(True)
    
    #sleep(1,3)
    #Check if rtc has invalid year, if so, automatically update rtc from portal
    checkClockYear()
    
    print "Startup Done!"
    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global secondCounter, minuteCounter
    secondCounter += 1
    if secondCounter >= 10:
        doEverySecond()      
        secondCounter = 0
        minuteCounter += 1
        if minuteCounter >= 60:
            doEveryMinute()
            minuteCounter = 0
    
def doEverySecond():
    #pass
    eventString = str(displayLMTempF()) + "," + str(displayLMTemp())
    print eventString
    print displayClockDT()
    #sleep(0,1)
    
    
def doEveryMinute():
    global datablock
    #address = datablock * 64
    global taddress
    
    eventString = str(displayClockDT()) + "," + str(displayLMTemp()) + "," + str(displayLMTempF()) + ",EOB"
    t = len(eventString)
    if (t < 32):
        index = t
        while (index < 32):
            eventString = eventString + "0"
            index += 1
    tt = len(eventString)
    writeEEblock(taddress, eventString)

    eventString = eventString + " " + str(t) + " " + str(taddress) + " " + str(tt)
    rpc(portalAddr, "logEvent", eventString)
    #if (t < 32):
    #    t = 32
    taddress += tt
    datablock += 1
    
    return getI2cResult()
    
@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    """Hooked into the HOOK_GPIN event"""
    #global timeFlag
    print str(pinNum),
    print str(isSet)
    eventString = "HOOK_GPIN " + str(pinNum) + str(isSet)
    rpc(portalAddr, "logEvent", eventString)
    
def testLogE():
    eventString = "Config: " + str(displayClockDT()) + ",EOB"
    t = len(eventString)
    #writeEEblock(taddress, eventString)
    writeEEblock(0, eventString)
    String2 = str(getI2cResult()) + " " + str(t)
    return String2

def sleepTest(mode, ticks):
    wakeupOn(GPIO_10, True, False)
    sleep(mode, ticks)
