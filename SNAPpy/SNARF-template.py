"""
filename.py   - template

CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

v201103261116 - template

"""

from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *
#from pcf2129a_m import *
#from lm75a_m import *
#from m24lc256_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
#portal_addr = None
secondCounter = 0 
minuteCounter = 0

#These are the GPIO pins used on the SNARF-BASE v3.h
VAUX = GPIO_5
RTC_INT = GPIO_10


@setHook(HOOK_STARTUP)
def start():    
    # Setup the Auxilary Regulator for sensors:
    setPinDir(VAUX, True)       #output
    writePin(VAUX, False)       #Turn off aux power
    # Setup the RTC Interrupt pin
    setPinDir(RTC_INT, False)   #Input
    #setPinPullup(RTC_INT, True) #Turn on pullup
    #monitorPin(RTC_INT, True)   #monitor changes to this pin. Will go low on int
    #wakeupOn(RTC_INT, True, False)  #Wake from sleep when pin goes low
    
    # I2C GPIO_17/18 rf100. rf200 needs external pullups.
    #i2cInit(True)
    # On startup try to get the portal address. 
    if portalAddr is None:
        mcastRpc(1, 5, "get_portal_logger")
    else:
        #getPortalTime()
        pass
    # Go ahead and redirect STDOUT to Portal now
    #ucastSerial(portal_addr) # put your correct Portal address here!
    #getPortalTime()
    #initUart(0,9600)
    #flowControl(0,False)
    #crossConnect(DS_STDIO,DS_UART0)
    
    #Check if rtc has invalid year, if so, automatically update rtc from portal
    #This is not a very robust check, but work for testing.
    #checkClockYear()
    
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
    rpc(portalAddr, "plotlq", loadNvParam(8), getLq(), 0)
    #rpc(portalAddr, "infoDT", displayClockDT())
    
def doEveryMinute():
    pass
    
@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    """Hooked into the HOOK_GPIN event"""
    #mostly debug and pointless irw
    print str(pinNum),
    print str(isSet)
    eventString = "HOOK_GPIN " + str(pinNum) + str(isSet)
    rpc(portalAddr, "logEvent", eventString)
    

def turnONVAUX():
    writePin(VAUX, True)       #Turn on aux power 

def turnOFFVAUX():
    writePin(VAUX, False)      #Turn off aux power

def set_portal_addr():
    """Set the portal SNAP address to the caller of this function"""
    global portalAddr
    portalAddr = rpcSourceAddr()
    #getPortalTime()



ADC_Offset = 0
DEGF = (30,33,35,337,39,41,43,45,47,49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,79,81,83,85,87,89)

def EnableTempSensor():
    # Set ADC channel
    value = peek(0x7c)
    value |= 0x09
    poke(0x7c, value)
    
    # Set Mux5 = 1
    value = peek(0x7b)
    value |= 0x08
    poke(0x7b, value)
    
    # Select ADC clock
    value = peek(0x7a)
    value |= 0x05   # CPU Clk/32 = 500kHz
    poke(0x7a, value)
    
    # Set ADMUX
    value = 0
    value |= 0xc0   # Set 1.6 Vref
    value |= 0x09   # Set MUX4
    poke(0x7c, value)
    
    # Set Tracking time
    value = peek(0x77)
    value &= 0x3F   # Tracking time = 0
                    # Use default setup time
    poke(0x77, value)
    
    # Enable ADC
    value = peek(0x7a)
    value |= 0x80
    poke(0x7a, value)
    
def startADC():
    # Begin conversion
    value = peek(0x7a)
    value |= 0x40
    poke(0x7a, value)
    
def readADC():
    # Read data registers
    Lbyte = peek(0x78)
    Hbyte = peek(0x79)
    val = Hbyte << 8 | Lbyte
    return val

def ReadRawTemperature():
    startADC()
    return readADC() - ADC_Offset

def ReadDegrees():
    val = ReadRawTemperature()
    if val > 239 and val < 272:
        return DEGF[val - 240]
    else:
        return 0

def SetADCOffset(val):
    global ADC_Offset
    ADC_Offset = val
    
def _checkADCFlag():
    value = peek(0x7a)
    if value & 0x10:
        return 1
    return 0
    
def _clearADCComplete():
    value = peek(0x7a)
    value &= 0xFF
    poke(0x7a, value)