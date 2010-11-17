from synapse.platforms import *
from synapse.switchboard import *
from ds2764_ss import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<

@setHook(HOOK_STARTUP)
def start():
    # Go ahead and redirect STDOUT to Portal now
    ucastSerial("\x00\x00\x01") # put your correct Portal address here!
    crossConnect(DS_STDIO,DS_TRANSPARENT)
        
    # I2C GPIO_17/18 used for MCP3424
    print "calling i2cInit"
    i2cInit(True)
    
@setHook(HOOK_100MS)
def triggeredAt100ms():
    DS2764FetchBasic()
    
@setHook(HOOK_1S)
def trigger():
    rpc(portalAddr, "logData", "Lipo voltage mV", getDSVoltage(), 4500)
    rpc(portalAddr, "logData", "Current draw mA", getDSCurrent(), 100)    
    rpc(portalAddr, "logData", "Bat remain power", getDSACurrent(), 1000)
    
    print "Lipo voltage --> " + str(getDSVoltage()) + "mV"
    print "Lipo current --> " + str(getDSCurrent()) + "mA"
    print "Lipo accumulated current --> " + str(getDSACurrent()) + "mAh"
    
    