from synapse.platforms import *
from synapse.switchboard import *
from pcf2129a_m import *
from lm75a_m import *
from m24lc256_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
secondCounter = 0 
minuteCounter = 0
datablock = 1

@setHook(HOOK_STARTUP)
def start():    
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    initUart(0,9600)
    flowControl(0,False)
    crossConnect(DS_STDIO,DS_UART0)
        
    # I2C GPIO_17/18 rf100. rf200 needs external pullups.
    i2cInit(True)
    
    #Check if rtc has invalid year, if so, automatically update rtc from portal
    checkClockYear()
    
    print "Startup Done!"
    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global secondCounter, minuteCounter
    secondCounter += 1
    if secondCounter >= 9:
        doEverySecond()      
        secondCounter = 0
        minuteCounter += 1
        if minuteCounter >= 59:
            doEveryMinute()
            minuteCounter = 0
    
def doEverySecond():
    
    eventString = str(displayLMTempF()) + "," + str(displayLMTemp())
    print eventString
    print displayClockDT()
    #sleep(0,1)
    
    
def doEveryMinute():
    global datablock
    address = datablock * 64
    eventString = str(displayClockDT()) + "," + str(displayLMTemp()) + "," + str(displayLMTempF()) + ",EOB"
    writeEEblock(address, eventString)
    datablock += 1
    
    
def testLogE():
    writeEEblock(0, displayClockDT())
    return getI2cResult()