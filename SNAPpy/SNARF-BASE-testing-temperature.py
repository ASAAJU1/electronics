"""
SNARF-BASE-testing-temperature.py   
                - Main script to test built in devices on board and
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
v201108181746 - modified for using snap connect and a commmand and control to request
                work to do when woke up.

"""

from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *
from pcf2129a_m import *
from lm75a_m import *
from m24lc256_m import *
from jc_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
e10Addr = '\x4c\x70\xbd'
snapc = '\xaa\xbb\xcc'
secondCounter = 0 
minuteCounter = 0
datablock = 1
taddress = 64
jcdebug = False
contactPortal = True
allowSleep = True

#These are the GPIO pins used on the SNARF-BASE v3.h
VAUX = GPIO_5
RTC_INT = GPIO_10
LED1 = GPIO_0

@setHook(HOOK_STARTUP)
def start():    
    global devName, devType
    global taddress
    devName = str(loadNvParam(8))
    devType = str(loadNvParam(10))
    setPinDir(LED1, True)

    # Setup the Auxilary Regulator for sensors:
    setPinDir(VAUX, True)       #output
    writePin(VAUX, False)       #Turn off aux power
    # Setup the RTC Interrupt pin
    setPinDir(RTC_INT, False)   #Input
    setPinPullup(RTC_INT, True) #Turn on pullup
    monitorPin(RTC_INT, True)   #monitor changes to this pin. Will go low on int
    wakeupOn(RTC_INT, True, False)  #Wake from sleep when pin goes low
    setPinDir(GPIO_9, False)
    
    # I2C GPIO_17/18 rf100. rf200 needs external pullups.
    i2cInit(True)
    initLM75A()
    # On startup try to get the portal address. 
    if portalAddr is None:
        mcastRpc(1, 5, "get_portal_logger")
    else:
        getPortalTime()
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial(portalAddr) # put your correct Portal address here!
    getPortalTime()
    #initUart(0,38400)
    #flowControl(0,False)
    crossConnect(DS_STDIO,DS_TRANSPARENT)
    
    #sleep(1,3)
    #Check if rtc has invalid year, if so, automatically update rtc from portal
    #This is not a very robust check, but work for testing.
    checkClockYear()
    #crossConnect(DS_STDIO,DS_TRANSPARENT)
    print "Startup Done!"
    #crossConnect(DS_STDIO,DS_UART0)
    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global secondCounter, minuteCounter
    secondCounter += 1
    #if secondCounter == 1:
    #    rpc(portalAddr, "plotlq", devName, getLq(), str(displayClockDT()))
    if secondCounter == 3:
        rpc(snapc, "getcmd2x")
    if secondCounter == 4:
        rpc(snapc, "getcmd2x")
    if secondCounter == 5:
        rpc(snapc, "getcmd2x")
    if secondCounter == 8:
        zCalcWakeTime2info()
    if secondCounter == 10:
        doEveryMinute()
    #if secondCounter > 5 and secondCounter < 20:
    #    rpc(portalAddr, "logEvent", secondCounter)
    if secondCounter >= 20 and allowSleep == True:
        #doEverySecond()    
        rpc(portalAddr, "logEvent", secondCounter)  
        secondCounter = 0
        sleep(1,180)
    if secondCounter >= 30 and secondCounter %10 == 0:
        rpc(snapc, "getcmd2x")
        if (contactPortal):
            rpc(portalAddr, "getcmd2x")
    if secondCounter >= 1200:
        secondCounter = 0
        #minuteCounter += 1
        #if minuteCounter >= 60:
        #    doEveryMinute()
        #    minuteCounter = 0
    
def doEverySecond():
    #pass
    global taddress
    dts = str(displayClockDT())
    eventString = dts + "," + str(displayLMTempF()) + "," + str(displayLMTemp()) + "," + str(taddress)
    print eventString
    rpc(portalAddr, "plotlq", devName, getLq(), dts)
    #rpc(portalAddr, "infoDT", displayClockDT())
    #print displayClockDT()
    #sleep(0,1)
    
    
def doEveryMinute():
    global datablock
    #address = datablock * 64
    global taddress
    
    #For testing, we log clockdate and time, temp C, temp F to half a page of eeprom
    dts = str(displayClockDT())
    buffer = readLM75(0,2)
    lm75a = (ord(buffer[0])) << 8 | ord(buffer[1])
    eventString = dts + "," + str(displayLMTemp()) + "," + str(displayLMTempF()) + ",EOB"
    t = len(eventString)
    if (t < 32):
        index = t
        while (index < 32):
            eventString = eventString + "0"
            index += 1
    tt = len(eventString)
    #writeEEblock(taddress, eventString)

    eventString2 = loadNvParam(8) + ": " + eventString + " " + str(t) + " " + str(taddress) + " " + str(tt)
    rpc(portalAddr, "logEvent", eventString2)
    rpc(portalAddr, 'graph_generic_lqdts', devName, displayLMTempF(), getLq(), dts)
    
    rpc(snapc, "logToCSV", devName, eventString)
    rpc(snapc, "loglm75aRawCalc", devName, str(lm75a))
    #if (t < 32):
    #    t = 32
    taddress += tt
    datablock += 1
    
    return getI2cResult()
    
@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    """Hooked into the HOOK_GPIN event"""
    #mostly debug and pointless irw
    print str(pinNum),
    print str(isSet)
    eventString = "HOOK_GPIN " + str(pinNum) + str(isSet)
    #rpc(portalAddr, "logEvent", eventString)
    
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

def set_portal_addr():
    """Set the portal SNAP address to the caller of this function"""
    global portalAddr
    portalAddr = rpcSourceAddr()
    getPortalTime()
def contactportalEnable():
    global contactPortal
    contactPortal = True
def contactportalDisable():
    global contactPortal
    contactPortal = False
def allowSleepEnable():
    global allowSleep
    allowSleep = True
def allowSleepDisable():
    global allowSleep
    allowSleep = False    
def csleep(a,b):
    sleep(int(a),int(b))