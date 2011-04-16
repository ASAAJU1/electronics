"""
#This function returns a result code from the following list:
#NV_SUCCESS = 0,
#// Possible LOAD errors
#NV_NOT_FOUND = 1,
#NV_DEST_TOO_SMALL = 2,
#// Possible SAVE errors
#NV_FULL = 3, // no more room in NV (even after "compression")
#NV_BAD_LENGTH = 4,
#NV_FAILURE = 5, // literally unable to write to FLASH (should never happen)
#NV_BAD_TYPE = 6, // invalid or unsupported data type
#NV_LOW_POWER = 7, // we refuse to even try if power is bad (low voltage)

"""
from synapse.nvparams import *
secondCounter = 0

@setHook(HOOK_STARTUP)
def start(): 
    global error
    error = 0
    error = saveNvParam(NV_NETWORK_ID, 0x1C2C)
    error += saveNvParam(NV_CHANNEL_ID, 4)
    error += saveNvParam(50, 0)
    error += saveNvParam(51, "F4Swu7Aruphewume")
    
    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global error
    global secondCounter, minuteCounter
    secondCounter += 1
    if (error):
        print error
    if secondCounter == 20:
        reboot()
        eraseImage()
