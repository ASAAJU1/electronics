"""
Program Description:    DS2764.py - Example I2C routines for the Maxim DS2764.

-------------------------------------------------------------------------------------------------
"""

from synapse.platforms import *
from synapse.switchboard import *
from synapse.hexSupport import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
DS2764_ADDRESS = 52<<1  #1slave address is 01101000 which shifts to 01101001(R/W)
retries = 1

buffer = 0
msLoopCounter = 0

#--------------------
# Startup Hook
#--------------------    

@setHook(HOOK_STARTUP)
def start():
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    crossConnect(DS_STDIO,DS_TRANSPARENT)
    
    # I2C GPIO_17/18 used for MCP3424
    i2cInit(True)
    initComplete = True
    
@setHook(HOOK_100MS)
def triggeredAt100ms():
    global buffer, msLoopCounter
    if msLoopCounter >= 5:        
        buffer = readDS2764(0x0C,6)   
        msLoopCounter = 0
             
    msLoopCounter += 1
    
        
def readDS2764(firstReg, numRegs):
    cmd = buildDSCmd(firstReg, False)
    i2cWrite(cmd, retries, False)    
    cmd = chr( DS2764_ADDRESS | 1 )
    return i2cRead(cmd, numRegs, retries, False)
    
def buildDSCmd(registerAddress, isRead):
    """internal helper routine"""
    slaveAddress = DS2764_ADDRESS
    if isRead:
        slaveAddress |= 1 # read        
 
    cmd = ""
    cmd += chr( slaveAddress )
    cmd += chr( registerAddress )
    return cmd    

def getDSVoltage():
    global buffer
    v = (ord(buffer[0])) << 8 | ord(buffer[1])
    v = v >> 6    
    v = (((v*61) / 10) * 8) / 10
    v = v << 1
    return v

def getDSCurrent():
    global buffer
    c = (ord(buffer[2]) << 8 ) | ord(buffer[3])
    c = c / 8 * 5 / 8
    return c

def getDSACurrent():
    ac = ((ord(buffer[4]) << 8) | ord(buffer[5])) / 4
    return ac

def getDSTemperature():
    buf = readDS2764(0x18,2)
    t = (ord(buf[0]) << 8) | ord(buf[1])
    t = t >> 5
    t = t / 8
    return t

def setDischargeEnable(bool):
    prot = readDS2764(0x00, 1)
    cmd = buildDSCmd(0x00, False)
    """ TODO This should read the current prot register first and then just flip the correct bit """
    cmd += (prot | 1) if (bool == True) else (prot & ~1)
    #return sendDS2764(cmd)

def setChargeEnable(bool):
    prot = ord(readDS2764(0x00, 1))
    cmd = buildDSCmd(0x00, False)
    """ TODO This should read the current prot register first and then just flip the correct bit """
    cmd += chr(prot | 2) if (bool == True) else chr(prot & ~2)
    return sendDS2764(cmd)

def setAccumulatedCurrent(mAhValue):
    writeVal = 4 * mAhValue
    msb = writeVal >> 8
    lsb = writeVal & 0xFF
        
    cmd = buildDSCmd(0x10, False)
    cmd += chr(msb)
    cmd += chr(lsb)
    return sendDS2764(cmd)

def clearDSProtRegister():
    cmd = buildDSCmd(0x00, False)    
    cmd = cmd + chr(0x03) 
    r = sendDS2764(cmd)   
    if r != 1:
        print "I2C error " + str(r)
        

def getDSProtRegister():
    bitSet = ord(readDS2764(0x00,1))
    return bitSet

def printDSProtRegister():
    bitSet = getDSProtRegister()
    binStr = ""
    # lookup = ["OV","UV","COC","DOC","CC","DC","CE","DE"]
    i = 0
    while i < 8:
        if (i == 0):
            binStr += "|"
        binStr += "1|" if (bitSet & 128) else "0|"        
        bitSet = bitSet << 1
        i = i+1
    return binStr
        
def sendDS2764(cmd):
    i2cWrite(cmd, retries, False)
    return getI2cResult()        
        
def byteToBinStr(b):
    i = 1
    binStr = ''
    while i <= 8:
        binStr += '1' if (b & 128) else '0'        
        b = b << 1
        i = i+1
    return binStr