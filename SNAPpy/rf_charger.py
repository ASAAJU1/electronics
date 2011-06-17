from synapse.platforms import *
from synapse.switchboard import *
from ds2764_ss import *
from pcf2129a_m import *
from synapse.hexSupport import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<

CHG_ERROR = GPIO_9
CHG_STATUS = GPIO_10

isChargingPreviousState = False
chgStatusBlinkTimer = 0
chgStatusBlinkCounter = 0

timeCount = 0
noSleep = True

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
    
    initUart(0, 19200)
    stdinMode(0, False)
    flowControl(0, False)
    crossConnect(DS_STDIO, DS_UART0)
    
    #ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    #crossConnect(DS_STDIO,DS_TRANSPARENT)
        
    # I2C GPIO_17/18 used for MCP3424
    i2cInit(True)
    
    chgStatusBlinkTimer = getMs()
    
    
@setHook(HOOK_GPIN)
def pinHandler(pin, isSet):
    global noChgError, chgStatusBlinkTimer, chgStatusBlinkCounter, isChargingPreviousState, chargeStatus
    if (pin == CHG_ERROR):
        noChgError = isSet
    if (pin == CHG_STATUS):
        chgStatusBlinkTimer = getMs()        
        if (isSet != isChargingPreviousState):
            chgStatusBlinkCounter += 1
        
        if (chgStatusBlinkCounter >=3):
            # charging complete
            chargeStatus = 'D'
            
            # Roll the value before we overflow
            if (chgStatusBlinkCounter >= 32767):
                chgStatusBlinkCounter = 3
                        
        isChargingPreviousState = isSet        
                     
def allowSleep():
    global noSleep
    noSleep = False
                  
def dontSleep():
    global noSleep
    noSleep = True              
                
@setHook(HOOK_100MS)
def triggeredAt100ms():
    global chargeStatus
    DS2764FetchBasic()
    
    # manage the charge status indicator timer    
    t = getMs()
    if (t > chgStatusBlinkTimer + 2500):      
        chargeStatus = 'N' if (readPin(CHG_STATUS)) else 'C'
    
def getChargeError():
    return True if (not noChgError) else False

def getChargeStatus():
    return chargeStatus

def getMyAddress():
    address = localAddr()
    return byteToHex(ord(address[0])) + "." + byteToHex(ord(address[1])) + "." + byteToHex(ord(address[2]))

def byteToHex(byte):
    value = str(hexNibble(byte >> 4)) + str(hexNibble(byte))
    return value
    
@setHook(HOOK_1S)
def trigger():
    global timeCount
    timeCount += 1
    cur = getDSCurrent()
    if (cur < 0):
        cur *= -1        
    
    # Only sample once per wakeup period
    if timeCount == 1:
        rpc('\x4C\x70\xBD', "Debuglog", getMyAddress()+","+str(getDSVoltage())+","+str(getDSTemperature())+","+str(getDSCurrent())+","+str(getDSACurrent()))
        print str(getDSVoltage())+","+str(getDSTemperature())+","+str(getDSCurrent())+","+str(getDSACurrent())
        
    # when in nosleep mode send data every 180 seconds
    if (noSleep and timeCount >= 300):
        timeCount = 0
    
    # stay awake for 10 seconds when in sleep mode
    if (not noSleep and timeCount >= 10):
         timeCount = 0
         sleep(1, 180)
         
    
    #print "Lipo mV -> " + str(getDSVoltage()) + "mV"
    #print "Lipo mA -> " + str(getDSCurrent()) + "mA"
    #print "Lipo mAh -> " + str(getDSACurrent()) + "mAh"    
    #print "Charging -> " + str(readPin(CHG_STATUS))
    #print "Charging error " + str(chg_error)
    