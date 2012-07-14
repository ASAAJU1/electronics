"""
Program Description:    PCF2129A_m.py - Example I2C routines for the NXP PCF2129A TXCO RTC.
This is a module meant to be imported.

CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

v201103061848   writeClockAlarm(Minute,Second) Sets the control register for an interrupt 
                to trigger at that time. Easily expandable to hours and date.
v201108181655   little updates
v201108221422   Start adding error checking/handling and application level verification
-------------------------------------------------------------------------------------------------
"""

PCF2129_ADDRESS = 81<<1 #slave address is 10100010 which shifts to 10100011(R/W)
retries = 1

def buildTWICmd(slaveAddress, registerAddress, isRead):
    """internal helper routine"""
    if isRead:
        slaveAddress |= 1 # read        
 
    cmd = chr( slaveAddress )
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
    """example routine to RPC to Portal logEvent the Time from RTC, can be modified to return string"""
    buff = readPCF2129(0x03,7)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    Hours = bcdToDec(ord(buff[2]) & 0x3F)
    Days = bcdToDec(ord(buff[3]) & 0x3F)
    DOW = bcdToDec(ord(buff[4]) & 0x07)
    Months = bcdToDec(ord(buff[5]) & 0x1F)
    Years = bcdToDec(ord(buff[6]))
    eventString = "Military Time: " + str(Hours) + ":" + str(Minutes) + ":" + str(Seconds)
    rpc(portalAddr, "logEvent", eventString)
    
def displayClockDate():
    """example routine to RPC to Portal the Date from RTC, can be modified to return string"""
    buff = readPCF2129(0x06,4)
    
    Date = bcdToDec(ord(buff[0]) & 0x3F)
    DOW = bcdToDec(ord(buff[1]) & 0x07)
    Month = bcdToDec(ord(buff[2]) & 0x1F)
    Year = bcdToDec(ord(buff[3]))
    
    eventString = "Date: " + str(displayDOW(DOW)) + " " + str(Month) + "/" + str(Date) + "/" + str(Year) 
    rpc(portalAddr, "logEvent", eventString)

def checkClockYear():
    """Very Crude routine to see if RTC has correct year, if not, request time from portal"""
    buff = readPCF2129(0x09,1)
    
    Year = bcdToDec(ord(buff[0]))
    if (Year <> 12):
        eventString = str(loadNvParam(8)) +": Invalid year: " + str(Year)
        rpc(portalAddr, "logEvent", eventString)
        getPortalTime()
    
def writeClockTime(Year,Month,Day,DOW,Hour,Minute,Second):
    global timeSynced
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
    t = getI2cResult()
    if t == 1:
        buff = readPCF2129(0x03,7)
        Seconds = bcdToDec(ord(buff[0]) & 0x7F)
        Minutes = bcdToDec(ord(buff[1]) & 0x7F)
        Hours = bcdToDec(ord(buff[2]) & 0x3F)
        Days = bcdToDec(ord(buff[3]) & 0x3F)
        DOW = bcdToDec(ord(buff[4]) & 0x07)
        Months = bcdToDec(ord(buff[5]) & 0x1F)
        Years = bcdToDec(ord(buff[6]))
        rpc(rpcSourceAddr(), "GClockDisplay", "NodeClock Set", Years, Months, Days, DOW, Hours, Minutes, Seconds)
        timeSynced = True
    if t == 2:
        #I2C Bus Busy
        getPortalTime()
    if t == 3:
        #I2C Bus Lost means some other device stole the I2C bus
        pass
    if t == 4:
        #I2C_BUS_STUCK means there is some sort of hardware or configuration problem
        pass
    if t == 5:
        #I2C_NO_ACK means the slave device did not respond properly
        pass
    return t

def writeClockAlarm(Minute,Second):
    # This section clears the Alarm INT and programs
    # This INT to go low when the alarm is triggered
    # Control_2
    cmd = buildTWICmd(PCF2129_ADDRESS, 0x01, False)
    cmd += chr(2)   #Turn on AIE BIT
    i2cWrite(cmd, retries, False)
    # end of section
    
    #This section Sets the Alarm time to trigger at: 
    cmd = buildTWICmd(PCF2129_ADDRESS, 0x0A, False)
    
    cmd += chr(decToBcd(int(Second)))
    cmd += chr(decToBcd(int(Minute)))
    cmd += chr(128) #cmd += chr(decToBcd(int(Hour)))
    cmd += chr(128) #cmd += chr(decToBcd(int(Day)))
    cmd += chr(128) #cmd += chr(decToBcd(int(DOW)))
    #dumpHex(cmd)
    i2cWrite(cmd, retries, False)
    return getI2cResult()

def displayClockDT():
    """returns a string of length 12 YYMMDDHHmmSS"""
    buff = readPCF2129(0x03,7)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    Hours = bcdToDec(ord(buff[2]) & 0x3F)
    Days = bcdToDec(ord(buff[3]) & 0x3F)
    DOW = bcdToDec(ord(buff[4]) & 0x07)
    Months = bcdToDec(ord(buff[5]) & 0x1F)
    Years = bcdToDec(ord(buff[6]))
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    eventString = str(Years) + str(Months) + str(Days) + str(Hours) + str(Minutes) + str(Seconds)
    #if (jcdebug):
    #    te = str(loadNvParam(8)) +":" + eventString
    #    rpc(portalAddr, "logEvent", te)
    return eventString

def displayDOW(DOW):
    if (DOW == 0):
        Day = "Sun"
    if (DOW == 1):
        Day = "Mon"
    if (DOW == 2):
        Day = "Tues"
    if (DOW == 3):
        Day = "Wed"
    if (DOW == 4):
        Day = "Thu"
    if (DOW == 5):
        Day = "Fri"
    if (DOW == 6):
        Day = "Sat"
    return Day

def decToBcd(val):
    return ( (val/10*16) + (val%10) ) 

def bcdToDec(val):
    return ( (val/16*10) + (val%16) )   

def getPortalTime():
    """ Call This to have Portal Set RTC"""
    #portalAddr = "\x4c\x70\xbd"
    #portalAddr = snap
    rpc(portalAddr, "setRFTime", localAddr())
    
    