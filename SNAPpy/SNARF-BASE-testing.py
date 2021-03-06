"""
SNARF-BASE-testing.py   - Main script to test built in devices on board and
                        - pinwake by rtc on RF100/200

CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

v201103062335 - Too many mods to log
v201103171943 - Set initial Portal Address to none. Add set_portal_addr() function
                Add the zCalcWakeTime1() function. 
v201103191511 - Would not compile without a portalAddr. So set portal as 1 and left
                Function to change portal addr.
v201103272322 - testing plotlq rpc call, modfied arguments
v201105311415 - modified for quick automated teasting
v201207131307 - move modules for better clarification in portal
"""

from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *
from contrib.jc.i2c.pcf2129a_m import *
from contrib.jc.i2c.lm75a_m import *
from contrib.jc.i2c.m24lc256_m import *
from contrib.jc.misc.jc_m import *
from contrib.jc.misc.jc_cnc_m import *

# Glabal vars
portalAddr = '\x00\x00\x02' # hard-coded address for Portal <------------<<<<<<<<
secondCounter = 0 
minuteCounter = 0
datablock = 1
taddress = 64
jcdebug = True
contactPortal = True
evenOdd = 0

#These are the GPIO pins used on the SNARF-BASE v3.h
VAUX = GPIO_5       # used to put secondary regulator in shutdown mode
RTC_INT = GPIO_10   # used to wake module
LED1 = GPIO_0       # used for testing purposes

@setHook(HOOK_STARTUP)
def start():    
    #global taddress
    global Dname, Dtype, devType, devName
    Dtype = str(loadNvParam(10))
    Dname = str(loadNvParam(8))
    devName = str(loadNvParam(8))
    devType = str(loadNvParam(10))

    setPinDir(LED1, True)           # output

    # Setup the Auxilary Regulator for sensors:
    setPinDir(VAUX, True)           #output
    writePin(VAUX, True)            #Turn off aux power
    # Setup the RTC Interrupt pin
    setPinDir(RTC_INT, False)       #Input
    setPinPullup(RTC_INT, True)     #Turn on pullup
    monitorPin(RTC_INT, True)       #monitor changes to this pin. Will go low on int
    wakeupOn(RTC_INT, True, False)  #Wake from sleep when pin goes low
    #setPinDir(GPIO_9, False)
    
    # I2C GPIO_17/18 rf100. rf200 usually needs external pullups.
    i2cInit(True)
    # On startup try to get the portal address if different from hard coded
    # This function needs contactPortal to be True
    findPortal()
    # Go ahead and redirect STDOUT to Portal now
    if (contactPortal):
        getPortalTime()
        # Go ahead and redirect STDOUT to Portal now
        ucastSerial(portalAddr) # put your correct Portal address here!
    #initUart(0,38400)
    #flowControl(0,False)
    crossConnect(DS_STDIO,DS_TRANSPARENT)
    #sleep(1,3)
    #Check if rtc has invalid year, if so, automatically update rtc from portal
    #This is not a very robust check, but works for testing.
    checkClockYear()
    #crossConnect(DS_STDIO,DS_TRANSPARENT)
    print "Startup Done!"
    #crossConnect(DS_STDIO,DS_UART0)
    
# Run every 100 MS. This is a standard counter/loop 
# to run events on seconds and minutes
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
    global taddress,evenOdd
    evenOdd += 1
    rpc(portalAddr,"getcmd2x")
    if (timeSynced == False):
        getPortalTime()
    dts = displayClockDT()
    #eventString = str(dts) + "," + str(displayLMTempF()) + "," + str(displayLMTemp()
    #eventString = displayClockDT() + "," + str(displayLMTemp()) + "," + str(displayLMTempF())
    #print eventString
    rpc(portalAddr, "plotlq", devName, getLq(), dts)
    if (contactPortal):
        rpc(portalAddr, "loglm75aRawCalc", devName, displayLMRaw())
    if (evenOdd % 2):
        zCalcWakeTimeinfo(1)
    else:
        gotoSleep(120)
    #rpc(portalAddr, "infoDT", displayClockDT())
    #print displayClockDT()
    #sleep(0,1)
    
    
def doEveryMinute():
    global datablock
    #address = datablock * 64
    global taddress
    
    #For testing, we log clockdate and time, temp C, temp F to half a page of eeprom
    eventString = str(displayClockDT()) + "," + str(displayLMTemp()) + "," + str(displayLMTempF()) + ",EOB"
    t = len(eventString)
    if (t < 32):
        index = t
        while (index < 32):
            eventString = eventString + "0"
            index += 1
    tt = len(eventString)
    writeEEblock(taddress, eventString)

    eventString = loadNvParam(8) + ": " + eventString + " " + str(t) + " " + str(taddress) + " " + str(tt)
    rpc(portalAddr, "logEvent", eventString)
    #if (t < 32):
    #    t = 32
    taddress += tt
    datablock += 1
    
    return getI2cResult()
    
#@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    """Hooked into the HOOK_GPIN event"""
    #mostly debug and pointless irw
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


def turnONVAUX():
    writePin(VAUX, True)       #Turn on aux power 

def turnOFFVAUX():
    writePin(VAUX, False)      #Turn off aux power

def addressPortal():
    """Set the portal SNAP address to the caller of this function"""
    global portalAddr
    portalAddr = rpcSourceAddr()
    getPortalTime()

def test_sleep():
    zCalcWakeTimeinfo(1)
    sleep(0,0)