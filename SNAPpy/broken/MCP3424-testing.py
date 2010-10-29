"""
Program Description:    MCP3424.py - Example I2C routines for the Microchip MCP3424 ADC.

Thanks:                 http://forums.adafruit.com/viewtopic.php?f=31&t=12269
 
-------------------------------------------------------------------------------------------------
"""

#from synapse.pinWakeup import *
from synapse.platforms import *
from synapse.switchboard import *


portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
LED_PIN = GPIO_1

MCP3424_ADDRESS = '\xD1' #1slave address is 01101000 which shifts to 11010001(R/W)
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
    MCP3424_init()
    
    
#-------------
# 100 ms Hook
#-------------

@setHook(HOOK_100MS)    
def timer100msEvent(currentMs):
    """On the 100ms tick, pulse the LED"""
    pulsePin(LED_PIN, 75, True)

def MCP3424_init():
    """Init the MCP3424"""
    i2cInit(True) # No pullups = false <--- Must be called on startup hook
    #print "ADC_Config: ",
    #print adcConfig
    #adcConfig |= chan << 5 | res << 2 | gain
    #mvDivisor = 1 << (gain + 2*res)
    #MCP3424_Write(adcConfig)
    #print "ADC_Config after write:",
    #print adcConfig
    
    
def MCP3424_Write(config):
    global MCP3424_ADDRESS
    cmd = ""
    cmd += ord(MCP3424_ADDRESS )
    cmd += ord(config)
    i2cWrite(cmd,retries,False)
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
    
    print ord(data[0])
    print ord(data[1])
    print ord(data[2])
    print ord(data[3])
    print ord( MCP3424_ADDRESS )
    print MCP3424_ADDRESS

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
    x = 60
    while x < 128:
        i2cRead(x,1,1,False)
        #print "Address: ",x,
        #print " result: ",
        #print getI2cResult()
        if(getI2cResult() == 1):
            print "A:",x
        #rpc(portalAddr, "logEvent", data)
        x += 1
    print "Done!"
    
    
    