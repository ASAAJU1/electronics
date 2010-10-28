"""
Program Description:    MCP3424.py - Example I2C routines for the Microchip MCP3424 ADC.

Thanks:                 http://forums.adafruit.com/viewtopic.php?f=31&t=12269
 

Author:                 JCWoltz
SubAuthor: 
Revision:               0.01
Date:                   10/26/2010
Snap Version:           2.1 or greater
Test on RF Engines:     RFE
Device:                 Maxim-IC I2C DS3231 RTC (Slave) Digikey Part #DS3231SN#-ND
                        Industry's most accurate Real Time Clock I2C RTC with integrated TCXO and 32.768 crystal
                        Crystal is accurate within +- 2 minutes per year.

RFET Pins:              GPIO 17 [RFET pin # 19] [SDA] & GPIO 18 [RFET pin # 20] [SCL]
                        DS3231 SOIC-16 Pins: SOIC pin #15 (SDA) & SOIC pin #16 (SCL) 
                         
Pullups:                External on the DS3231 proto board 4.7 K  - Do Not set the software pullups True 
                        (default - i2cInit(False)
                        
Working Status:         Ok - no bugs except doing multi register reads using readClock(firstReg, numRegs)
                        does not work? Single register reads will do the job.

Program Operation:      Steps:
                        1. Hookup the DS3231 SCL and SDA I/O to the RFET I/O pins 
                           I2C SCL clock DS3231 SOIC16  pin #16 to RFET Pin #20 [GPIO_18]
                           I2C SDA data  DS3231 SOIC16  pin #15 to REET Pin #19 [GPIO_17]
                        2. Pull up both I/O lines to Vcc using 1.5K to 4.7K resistors <--- we used.
                        3. Hookup up power and ground to the DS3231 RTC
                        4. Do not use the internal pullups - the starup hook
                           should call the DS3231_initRTC() which disables the pullups
                        5. Set the DS3231 RTC with the function
                           setTimeDate(hourINT,minuteINT,secondINT,dowINT,monthINT,dateINT,yearINT)
                           Note: Be sure to set the time in Military time! and include all settings eg DOW
                        6. Display or read the DS3231 RTC time/ date back using functions:          
                           getTimeDate(), displayClockDate() & displayClockTime()
                        7. Do not modify this code!
                        
                        Note: If the battery backup to the DS3231 is not used - just ground it.
                        To keep the RTC contents after power failure hook up the battery to the RTC.       

Future Enhancements:    Civilian Time AM/PM, both alarms with interrupt trigger
                        Range or input user checking - low priority.
                        Input error checking for time/date setup - low priority


-------------------------------------------------------------------------------------------------
"""

#from synapse.pinWakeup import *
from synapse.platforms import *
from synapse.switchboard import *


portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<

LED_PIN = GPIO_1


MCP3424_ADDRESS = '\x68' # slave address is 01101000 which shifts to 11010000(R/W)

retries = 1

# Glocal MCP3424 fields in config register
MCP3424_GAIN_FIELD  = '\x03'
MCP3424_GAIN_X1     = '\x00'
MCP3424_GAIN_X2     = '\x01'
MCP3424_GAIN_X4     = '\x02' # PGA gain X4
MCP3424_GAIN_X8     = '\x03' # PGA gain X8

MCP3424_RES_FIELD   = '\x0C' # resolution/rate field
MCP3424_RES_SHIFT   = 2   # shift to low bits
MCP3424_12_BIT      = '\x00' # 12-bit 240 SPS
MCP3424_14_BIT      = '\x04' # 14-bit 60 SPS
MCP3424_16_BIT      = '\x08' # 16-bit 15 SPS
MCP3424_18_BIT      = '\x0C' # 18-bit 3.75 SPS

MCP3424_CONTINUOUS  = '\x10' # 1 = continuous, 0 = one-shot

MCP3424_CHAN_FIELD  = '\x60' # channel field
MCP3424_CHANNEL_1   = '\x00' # select MUX channel 1
MCP3424_CHANNEL_2   = '\x20' # select MUX channel 2
MCP3424_CHANNEL_3   = '\x40' # select MUX channel 3
MCP3424_CHANNEL_4   = '\x60' # select MUX channel 4

MCP3424_START       = '\x80' # write: start a conversion
MCP3424_BUSY        = '\x80' # read: output not ready

#int adcConfig 
adcConfig = ord( MCP3424_START ) | ord( MCP3424_CHANNEL_1 ) | ord( MCP3424_CONTINUOUS )
mvDivisor = 1

 
BUTTON_PIN    = GPIO_5

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<

# Since there are currently no ZIC2410 based SNAP Engines,
# there are currently no GPIO on ZIC2410, just plain IO.
if platform == "ZIC2410":
    LED_PIN = 1
else:
    LED_PIN = GPIO_1
 
#--------------------
# Startup Hook
#--------------------    

@setHook(HOOK_STARTUP)
def start():
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    crossConnect(DS_STDIO,DS_TRANSPARENT)
    
    global BUTTON_PIN
    global LED_PIN
    
    # Initialize LED pin as output - GPIO 1
    setPinDir(LED_PIN, True) # SN171 LED #1 GRN (right)
    writePin(LED_PIN, False)
    
    # Initialize all non user pins to output/low for minimum power consumption
    setPinDir(GPIO_0, True) # Mailbox output to Gator
    writePin(GPIO_0, False) 
    
    setPinDir(GPIO_2, True) # SN171 LED #2  YEL (left)
    writePin(GPIO_2, False)
    
    setPinDir(GPIO_3, True) # OUTPUT - PIR LED Status
    writePin(GPIO_3, False)
    
    setPinDir(GPIO_4, False) # INPUT - PIR digital input
    #setPinPullup(GPIO_4,True) # Pullup input pin
    #writePin(GPIO_4, False)
    
    setPinDir(BUTTON_PIN, False)     # Input for Button Pin Tac switch 
    setPinPullup(BUTTON_PIN, True)   # Pullup Button Pin switch GPIO 5
    
    setPinDir(GPIO_6, True)
    writePin(GPIO_6, False)
    
    setPinDir(GPIO_7, False)         # Uart 1 Input - connected on 171 board
    #writePin(GPIO_7, True)
    
    setPinDir(GPIO_8, True)          # Uart 1 Output - connected on 171 board
    writePin(GPIO_8, False)
    
    setPinDir(GPIO_9, True)
    writePin(GPIO_9, False)
    
    setPinDir(GPIO_10, True)   
    writePin(GPIO_10, False)
    
    #setPinDir(GPIO_11, True)        # Analog 7
    #writePin(GPIO_11, False)
    
    #setPinDir(ADC_PIN, False)        # NOT an output - Analog input - Battery monitor
    
    #setPinDir(GPIO_12, True)        # Analog 6 - GPIO for battery monitor enable
    #writePin(GPIO_12, True)
    
    #setPinDir(Bat_Mon_Enable, True)  # Is an output
    #writePin(Bat_Mon_Enable, True)   # default to powering the battery monitor circuit

    
    setPinDir(GPIO_13, True)         # Analog 5
    writePin(GPIO_13, False)
    
    setPinDir(GPIO_14, True)         # Analog 4
    writePin(GPIO_14, False)
    
    setPinDir(GPIO_15, True)         # Analog 3
    writePin(GPIO_15, False)
    
    setPinDir(GPIO_16, True)         # Analog 2
    writePin(GPIO_16, False)
    
    # I2C GPIO_17/18 used for DS3231
    MCP3424_init()                 # <----- NEEDED--<<<<<  Init I2C RTC - no pullups
    
    
#-------------
# 100 ms Hook
#-------------

@setHook(HOOK_100MS)    
def timer100msEvent(currentMs):
    """On the 100ms tick, pulse the LED"""
    pulsePin(LED_PIN, 75, True)
      


def buildRtcCmd(registerAddress, isRead):
    """internal helper routine"""
    slaveAddress = MCP3424_ADDRESS
    if isRead:
        slaveAddress |= 1 # read

    cmd = ""
    cmd += chr( slaveAddress )
    cmd += chr( registerAddress )

    return cmd

def MCP3424_init():
    """Init just the MCP3424 (assumes i2cInit() already done)"""
    global adcConfig
    global mvDivisor
    i2cInit(True) # No pullups = false <--- Must be called on startup hook
    # Note we do not automatically setDate(), setTime()!
    chan = 0XFF
    gain = 0XFF 
    res = 0XFF
    # now set the actual
    chan = 0
    gain = 0
    res = 0
    print "ADC_Config: ",
    print adcConfig
    adcConfig |= chan << 5 | res << 2 | gain
    mvDivisor = 1 << (gain + 2*res)
    MCP3424_Write(adcConfig)
    #print "ADC_Config after write:",
    #print adcConfig
    
    
def MCP3424_Write(config):
    global MCP3424_ADDRESS
    #cmd = ""
    #cmd += ord(MCP3424_ADDRESS )
    #cmd += ord(config)
    cmd = '\x69\x8C'
    i2cWrite(cmd,2,True)
    print "Address: ",
    print MCP3424_ADDRESS,
    print " Config: ",
    print config,
    print " Cmd: ",
    print cmd,
    print " Result: ",
    print getI2cResult()

    
    
def MCP3424_Read():
    global MCP3424_ADDRESS
    data = i2cRead( MCP3424_ADDRESS, 4, 1, False)
    rpc(portalAddr, "logEvent", data)
    
    #print ord(data[0])
    #print ord(data[1])
    #print ord(data[2])
    #print ord(data[3])
    #print chr( MCP3424_ADDRESS )
    #print MCP3424_ADDRESS
    
    
    
    return getI2cResult()

def jtest():
    print adcConfig
    print ord( MCP3424_START )
    print ord( MCP3424_CHANNEL_1 )
    print ord( MCP3424_CONTINUOUS )
    
    adcConfig2 = ord( MCP3424_START ) 
    adcConfig2 += ord( MCP3424_CHANNEL_1 ) 
    adcConfig2 += ord( MCP3424_CONTINUOUS )
    
    print adcConfig2
    
def scani():
    x = 0
    while x < 128:
        i2cRead(x,1,1,False)
        if(getI2cResult()):
            print "Address: ",x
        x -= 1
    print "Done!"
    
    
    