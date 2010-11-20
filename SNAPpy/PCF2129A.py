"""
Program Description:    PCF2129A.py - Example I2C routines for the NXP PCF2129A TXCO RTC.

-------------------------------------------------------------------------------------------------
"""

#from synapse.pinWakeup import *
from synapse.platforms import *
from synapse.switchboard import *
from synapse.hexSupport import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
LED_PIN = GPIO_0

PCF2129_ADDRESS = 81<<1 #slave address is 10100010 which shifts to 10100011(R/W)
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
    
    # I2C GPIO_17/18
    i2cInit(True)
    
    
#-------------
# 100 ms Hook
#-------------

@setHook(HOOK_100MS)    
def timer100msEvent(currentMs):
    """On the 100ms tick, pulse the LED"""
    pulsePin(LED_PIN, 25, True)

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
    return result

def displayClockTime():
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
    
def displayClockDate():
    buffer = readPCF2129(0x06,4)
    
    Date = bcdToDec(ord(buffer[0]) & 0x3F)
    DOW = bcdToDec(ord(buffer[1]) & 0x07)
    Month = bcdToDec(ord(buffer[2]) & 0x1F)
    Year = bcdToDec(ord(buffer[3]))
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
    
def decToBcd(val):
    return ( (val/10*16) + (val%10) ) 

def bcdToDec(val):
    return ( (val/16*10) + (val%16) )   

def getPortalTime():
    """ Call This to have Portal Set RTC"""
    rpc(portalAddr, "setRFTime", localAddr())
    