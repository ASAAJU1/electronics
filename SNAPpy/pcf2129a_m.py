"""
Program Description:    PCF2129A.py - Example I2C routines for the NXP PCF2129A TXCO RTC.

-------------------------------------------------------------------------------------------------
"""

PCF2129_ADDRESS = 81<<1 #slave address is 10100010 which shifts to 10100011(R/W)

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
    buff = readPCF2129(0x03,7)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    Hours = bcdToDec(ord(buff[2]) & 0x3F)
    Days = bcdToDec(ord(buff[3]) & 0x3F)
    DOW = bcdToDec(ord(buff[4]) & 0x07)
    Months = bcdToDec(ord(buff[5]) & 0x1F)
    Years = bcdToDec(ord(buff[6]))
    eventString = "Military Time: " + str(Hours) + ":" + str(Minutes) + ":" + str(Seconds) + " DOW = " + str(DOW) 
    rpc(portalAddr, "logEvent", eventString)
    
def displayClockDate():
    buff = readPCF2129(0x06,4)
    
    Date = bcdToDec(ord(buff[0]) & 0x3F)
    DOW = bcdToDec(ord(buff[1]) & 0x07)
    Month = bcdToDec(ord(buff[2]) & 0x1F)
    Year = bcdToDec(ord(buff[3]))
    eventString = "Date: " + str(Month) + "/" + str(Date) + "/" + str(Year) 
    rpc(portalAddr, "logEvent", eventString)

def checkClockYear():
    buff = readPCF2129(0x09,1)
    
    Year = bcdToDec(ord(buff[0]))
    if (Year <> 10):
        getPortalTime()
    
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

def displayClockDT():
    buff = readPCF2129(0x03,7)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    Hours = bcdToDec(ord(buff[2]) & 0x3F)
    Days = bcdToDec(ord(buff[3]) & 0x3F)
    DOW = bcdToDec(ord(buff[4]) & 0x07)
    Months = bcdToDec(ord(buff[5]) & 0x1F)
    Years = bcdToDec(ord(buff[6]))
    eventString = str(Years) + str(Months) + str(Days) + str(Hours) +  str(Minutes) + str(Seconds)
    #rpc(portalAddr, "logEvent", eventString)
    return eventString

def decToBcd(val):
    return ( (val/10*16) + (val%10) ) 

def bcdToDec(val):
    return ( (val/16*10) + (val%16) )   

def getPortalTime():
    """ Call This to have Portal Set RTC"""
    rpc(portalAddr, "setRFTime", localAddr())
    