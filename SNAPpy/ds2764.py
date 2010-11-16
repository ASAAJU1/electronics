"""
Program Description:    DS2764.py - Example I2C routines for the Maxim DS2764.

-------------------------------------------------------------------------------------------------
"""

#from synapse.pinWakeup import *
from synapse.platforms import *
from synapse.switchboard import *
from synapse.hexSupport import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
LED_PIN = GPIO_0

DS2764_ADDRESS = 52<<1  #1slave address is 01101000 which shifts to 01101001(R/W)
retries = 1

#--------------------
# Startup Hook
#--------------------    

@setHook(HOOK_STARTUP)
def start():
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    crossConnect(DS_STDIO,DS_TRANSPARENT)
    
    global LED_PIN
    
    # Initialize LED pin as output - GPIO 1
    setPinDir(LED_PIN, True) # SN171 LED #1 GRN (right)
    writePin(LED_PIN, False)
    
    # I2C GPIO_17/18 used for MCP3424
    i2cInit(True)
    
    
#-------------
# 100 ms Hook
#-------------

@setHook(HOOK_100MS)    
def timer100msEvent(currentMs):
    """On the 100ms tick, pulse the LED"""
    pulsePin(LED_PIN, 75, True)
    
def readDS2764(firstReg, numRegs):
    cmd = buildDSCmd(firstReg, False)
    #dumpHex(cmd)
    i2cWrite(cmd, retries, False)
    #print getI2cResult()
    
    cmd = chr( DS2764_ADDRESS | 1 )
    #dumpHex(cmd)
    result = i2cRead(cmd, numRegs, retries, False)

    dumpHex(result)
    #print getI2cResult()
    return result
    
def buildDSCmd(registerAddress, isRead):
    """internal helper routine"""
    slaveAddress = DS2764_ADDRESS
    if isRead:
        slaveAddress |= 1 # read        
 
    cmd = ""
    cmd += chr( slaveAddress )
    cmd += chr( registerAddress )
    return cmd

def readDSVoltage():
    voltage = readDS2764(0x0C,2)
    dumpHex(voltage)
    voltage = int(voltage) >> 5
    #voltage = voltage * 4.88
    return voltage