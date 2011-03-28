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
v201103231616 - modified to test the atmega addon board. We start with the VAUX on
                as that powers the SD CARD.

"""

from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *
from synapse.sysInfo import *
from pcf2129a_m import *
from lm75a_m import *
from m24lc256_m import *
from jc_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
#portal_addr = None
secondCounter = 0 
minuteCounter = 0
datablock = 1
taddress = 64

#These are the GPIO pins used on the SNARF-BASE v3.h
#This has been tested with RF100 and RF200
#on RF200, This pin works, but consumes more power than it could
VAUX = GPIO_5
RTC_INT = GPIO_10


@setHook(HOOK_STARTUP)
def start():    
    # Setup the Auxilary Regulator for sensors:
    setPinDir(VAUX, True)           #output
    writePin(VAUX, True)            #Turn on aux power
    #VAUX needs to be on initially to initialize SD Card
    
    # Setup the RTC Interrupt pin
    setPinDir(RTC_INT, False)       #Input
    setPinPullup(RTC_INT, True)     #Turn on pullup
    monitorPin(RTC_INT, True)       #monitor changes to this pin. Will go low on int
    wakeupOn(RTC_INT, True, False)  #Wake from sleep when pin goes low
    
    # I2C GPIO_17/18 rf100. rf200 needs external pullups.
    i2cInit(True)
    # On startup try to get the portal address. 
    if portalAddr is None:
        mcastRpc(1, 5, "get_portal_logger")
    else:
        getPortalTime()
    # Go ahead and redirect STDOUT to Portal now
    #ucastSerial(portal_addr) # put your correct Portal address here!
    getPortalTime()
    initUart(1,9600)
    flowControl(1,False)
    crossConnect(DS_STDIO, DS_UART1)
    # send errors to portal
    uniConnect(DS_PACKET_SERIAL, DS_ERROR)
    
    devName = loadNvParam(8)  # get the device name
    
    #Test to try and catch any output/errors from addon
    #possible future addon for 2way comm
    stdinMode(0, False)      # Line Mode, Echo Off
        

    
    #sleep(1,3)
    #Check if rtc has invalid year, if so, automatically update rtc from portal
    #This is not a very robust check, but work for testing.
    checkClockYear()
    
    print "Startup Done!"
    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    pass
    #global secondCounter
    #secondCounter += 1
    #if secondCounter >= 10:
    #    doEverySecond()      
    #    secondCounter = 0
    
    
@setHook(HOOK_1S) 
def doEverySec(tick): 
    global minuteCounter
    minuteCounter += 1
    doEverySecond()
    if minuteCounter >= 60:
        #doEveryLongLog()
        minuteCounter = 0

#@setHook(HOOK_STDIN) 
def getInput(data): 
    ''' Process command line input '''
    pass
    global cmd, arg
    if data == '?':
        #help()
        pass
    elif len(data):
        getCmdArg(data)
        ret = None
        print
        
        if arg != None:
            ret = cmd(arg)
        else:
            ret = cmd()
    
        if ret != None:
            print " => ", ret
            
    print "\r\n>",
    

#@setHook(HOOK_RPC_SENT) 
def rpcDone(bufRef): 
    if bufRef == myRpcID:
      #You know this particular RPC has been sent
      pass
    pass
    #print str(bufRef)

def doEverySecond():
    #pass
    global taddress
    global portalAddr
    global myRpcID
    eventString = str(displayClockDT()) + "," + str(displayLMTempF()) + "," + str(displayLMTemp()) + "," + str(taddress)
    print eventString
    rpc(portalAddr, "plotlq", loadNvParam(8), getLq())
    myRpcID = getInfo(9)
    rpc(portalAddr, "infoDT", displayClockDT())
    myRpcID = getInfo(9)
    #print displayClockDT()
    #sleep(0,1)
    
    
def doEveryLongLog():
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

    eventString = eventString + " " + str(t) + " " + str(taddress) + " " + str(tt)
    rpc(portalAddr, "logEvent", eventString)
    #if (t < 32):
    #    t = 32
    taddress += tt
    datablock += 1
    zCalcWakeTime10()
    turnOFFVAUX()
    sleep(0,0)
    turnONVAUX()
    
    return getI2cResult()
    
@setHook(HOOK_GPIN)
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

def set_portal_addr():
    """Set the portal SNAP address to the caller of this function"""
    global portalAddr
    portalAddr = rpcSourceAddr()
    getPortalTime()

def getCmdArg(input):
    """Parse out a single int or string argument from given command-line input"""
    global cmd, arg
    cmd = ''
    arg = None
    i = 0
    while i < len(input):
        c = input[i]
        if c == ' ':
            if '0' <= input[i+1] <= '9':
                arg = int(input[i:])
                input = cmd
            else:
                arg = input[i+1:]
                input = cmd
            break

        cmd += c
        i += 1

def ver():
    print "SNAP v", getInfo(SI_TYPE_VERSION_MAJOR), '.', getInfo(SI_TYPE_VERSION_MINOR)
    print "Device Type: ", loadNvParam(10)
    
def echo(text):
    print text
    
@setHook(HOOK_STDIN)    
def stdinEventd(data):
    ''' Process command line input '''
    rpc(portalAddr, "logEvent", data)