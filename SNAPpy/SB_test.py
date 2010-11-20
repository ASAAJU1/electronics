from synapse.platforms import *
from synapse.switchboard import *
from ds2764_ss import *
from pcf2129a_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<

CHG_ERROR = GPIO_9
CHG_STATUS = GPIO_10

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
    global noChgError, chgStatusBlinkTimer, isChargingPreviousState
    setPinDir(CHG_ERROR, False)
    setPinDir(CHG_STATUS, False)
    monitorPin(CHG_ERROR, True)
    monitorPin(CHG_STATUS, True)
    
    noChgError = readPin(CHG_ERROR)
    isChargingPreviousState = readPin(CHG_STATUS)
    
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    crossConnect(DS_STDIO,DS_TRANSPARENT)
        
    # I2C GPIO_17/18 used for MCP3424
    i2cInit(True)
    
    #Check if rtc has invalid yer, if so, automatically update rtc from portal
    checkClockYear()
    
    chgStatusBlinkTimer = getMs()
    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global secondCounter
    secondCounter += 1
    if secondCounter >= 10:
        doEverySecond()      
        secondCounter = 0

def doEverySecond():
    DS2764FetchBasic()
    cur = getDSCurrent()
    if (cur < 0):
        cur *= -1
    rpc(portalAddr, "logData", "Lipo voltage mV", getDSVoltage(), 4500)
    rpc(portalAddr, "logData", "Current draw mA", cur, 400)    
    rpc(portalAddr, "logData", "Bat remain power", getDSACurrent(), 1000)
    eventString = displayClockDT() + "," + str(getDSVoltage()) + "," + str(getDSCurrent()) + "," + str(getDSACurrent())
    print eventString
    
    #print "Lipo mV -> " + str(getDSVoltage()) + "mV"
    #print "Lipo mA -> " + str(getDSCurrent()) + "mA"
    #print "Lipo mAh -> " + str(getDSACurrent()) + "mAh"    
    #print "Charging -> " + str(readPin(CHG_STATUS))
    #print "Charging error " + str(chg_error)
    
    