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

DS2764_ADDRESS = 52<<1  #slave address is 01101000 which shifts to 01101001(R/W)
PCF2129_ADDRESS = 81<<1 #slave address is 10100010 which shifts to 10100011(R/W)
retries = 1
buffer = 0

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
    
    # I2C GPIO_17/18
    i2cInit(True)
    
    #Test TX
    #mcastRpc(1,1, "testTx")
    #rpc(portalAddr, setButtonCount, 5)

    
#-------------
# 100 ms Hook
#-------------

@setHook(HOOK_100MS)    
def timer100msEvent(currentMs):
    """On the 100ms tick, pulse the LED"""
    #pulsePin(LED_PIN, 25, True)

#--------------
# RPC_Sent Hook
#--------------
#@setHook(HOOK_RPC_SENT)
#def rpcSentEvent(bufRef):
#    mcastRpc(1,1, "testTx")

def buildTWICmd(slaveAddress, registerAddress, isRead):
    """internal helper routine"""
    if isRead:
        slaveAddress |= 1 # read        
 
    cmd = ""
    cmd += chr( slaveAddress )
    cmd += chr( registerAddress )
    return cmd
 
def readDS2764(firstReg, numRegs):
    """read registers starting at firstReg and numRegs"""
    cmd = buildTWICmd(DS2764_ADDRESS, firstReg, False)
    #dumpHex(cmd)
    i2cWrite(cmd, retries, False)
    #print getI2cResult()
    
    cmd = chr( DS2764_ADDRESS | 1 )
    #dumpHex(cmd)
    result = i2cRead(cmd, numRegs, retries, False)

    #dumpHex(result)
    return result

def readPCF2129(firstReg, numRegs):
    """read registers starting at firstReg and numRegs"""
    cmd = buildTWICmd(PCF2129_ADDRESS, firstReg, False)
    #dumpHex(cmd)
    i2cWrite(cmd, retries, False)
    #print getI2cResult()
    
    cmd = chr( PCF2129_ADDRESS | 1 )
    #dumpHex(cmd)
    result = i2cRead(cmd, numRegs, retries, False)

    #dumpHex(result)
    #print getI2cResult()
    return result

def displayClockTime():
    global buffer
    buffer = readPCF2129(0x03,7)
    
    Seconds = bcdToDec(ord(buffer[0]) & 0x7F)
    Minutes = bcdToDec(ord(buffer[1]) & 0x7F)
    Hours = bcdToDec(ord(buffer[2]) & 0x3F)
    Days = bcdToDec(ord(buffer[3]) & 0x3F)
    DOW = bcdToDec(ord(buffer[4]) & 0x07)
    Months = bcdToDec(ord(buffer[5]) & 0x1F)
    Years = bcdToDec(ord(buffer[6]))
    eventString = "Military Time: " + str(Hours) + ":" + str(Minutes) + ":" + str(Seconds) + " DOW = " + str(DOW) 
    rpc(portalAddr, "logEvent", eventString)
    
    #print str(Hours),":",str(Minutes),":",str(Seconds),
    #print " ",str(Years),"/",str(Months),"/",str(Days)," ",str(DOW)
def displayClockDate():
    global buffer
    buffer = readPCF2129(0x03,7)
    
    Seconds = bcdToDec(ord(buffer[0]) & 0x7F)
    Minutes = bcdToDec(ord(buffer[1]) & 0x7F)
    Hours = bcdToDec(ord(buffer[2]) & 0x3F)
    Date = bcdToDec(ord(buffer[3]) & 0x3F)
    DOW = bcdToDec(ord(buffer[4]) & 0x07)
    Month = bcdToDec(ord(buffer[5]) & 0x1F)
    Year = bcdToDec(ord(buffer[6]))
    eventString = "Date: " + str(Month) + "/" + str(Date) + "/" + str(Year) 
    rpc(portalAddr, "logEvent", eventString)
    
def writeClockTime(Year,Month,Day,DOW,Hour,Minute,Second):
    cmd = buildTWICmd(PCF2129_ADDRESS, 0x03, False)
    cmd += chr(decToBcd(int(Second)))
    cmd += chr(decToBcd(int(Minute)))
    cmd += chr(decToBcd(int(Hour)))
    cmd += chr(decToBcd(int(Day)))
    cmd += chr(decToBcd(int(DOW)))
    cmd += chr(decToBcd(int(Month)))
    cmd += chr(decToBcd(int(Year)))
    #dumpHex(cmd)
    i2cWrite(cmd, retries, False)
    return getI2cResult()

def writeDS2764(Reg, Value):
    """Write to a register on the DS2764"""
    cmd = buildTWICmd(DS2764_ADDRESS, Reg, False)
    cmd += chr( Value )
    dumpHex(cmd)
    i2cWrite(cmd, retries, False)
    print getI2cResult()
    
    return getI2cResult()
 
def getDSVoltage():
    """Returns Battery Voltage"""
    voltage = readDS2764(0x0C,2)
    msb = ord(voltage[0])
    lsb = ord(voltage[1])
    v = (msb<<8) | lsb
    # Value to be multiplied by 4.88mV
    #v = v >> 5
    #v = v / 100
    #v = v * 488
    # workaround to avoid any step larger than 2^15
    #512*61=31232/10=3123*8=24984/10=2498<<1=4996
    v = v >> 6
    v = v*61
    v=v/10
    v=v*8
    v=v/10
    v=v<<1
    
    return v

def getDSCurrent():
    """Returns the Current reading"""
    current = readDS2764(0x0E,2)
    #dumpHex(current)
    msb = ord(current[0])
    lsb = ord(current[1])
    c = (msb<<8) | lsb
    c = c / 8
    c = c * 5
    c = c / 8
    return c

def getDSACurrent():
    """Returns The Accumulated Current"""
    acurrent = readDS2764(0x10,2)
    #dumpHex(acurrent)
    msb = ord(acurrent[0])
    lsb = ord(acurrent[1])
    ac = (msb<<8) | lsb
    ac = ac / 4
    return ac

def getDSTemperature():
    """Returns the Temperature Celcius from the DS2764"""
    #shift right 5 bits. multiply by 0.125 for degree C
    temp = readDS2764(0x18,2)
    msb = ord(temp[0])
    lsb = ord(temp[1])
    t = (msb<<8) | lsb
    t = t >> 5
    t = t / 8
    return t

def printDS2764Stats():
    print "Voltage: ",getDSVoltage(),
    print "mV, Current: ",getDSCurrent(),
    print "mA, Accumulated Current: ",getDSACurrent(),
    print "mAH"
    
def printDSProtectState():
    """Prints out the Protection Register Status"""
    tmp = readDS2764(0x00,2)
    p = ord(tmp[0])
    s = ord(tmp[1])
    if (p & 0x80):
        print "Over Voltage, ",
    if (p & 0x40):
        print "Under Voltage, ",
    if (p & 0x20):
        print "Charging Over Current, ",
    if (p & 0x10):
        print "Discharging Over Current, ",
    if (p & 0x08):
        print "CC, ",
    if (p & 0x04):
        print "DC, ",
    if (p & 0x02):
        print "Charging Enabled, ",
    if (p & 0x01):
        print "Discharging Enabled, ",
    if (s & 0x20):
        print "Sleep Mode Enabled"
    
    
def decToBcd(val):
    return ( (val/10*16) + (val%10) ) 

def bcdToDec(val):
    return ( (val/16*10) + (val%16) )   

def getPortalTime():
    rpc(portalAddr, "setRFTime", localAddr())
    