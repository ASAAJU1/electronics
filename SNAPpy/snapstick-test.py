#from synapse.evalBase import *
from synapse.platforms import *

#Globals
portalAddr=''
portalConnected = False
contactPortal = True
secondCounter = 0
redLEDPin = GPIO_0
greenLEDPin = GPIO_1   

@setHook(HOOK_STARTUP)
def startupEvent():
    """This is hooked into the HOOK_STARTUP event"""
    global devName, devType
    devName = str(loadNvParam(8))
    devType = str(loadNvParam(10))
    # set the LED pins to be 'outputs'  
    setPinDir(redLEDPin, True)
    setPinDir(greenLEDPin, True)  
    grnoff()
    redon()
    setPinDir(GPIO_5, False)
    setPinDir(GPIO_9, False)
    setPinDir(GPIO_10, False)
    monitorPin(GPIO_5, True)
    monitorPin(GPIO_9, True)
    monitorPin(GPIO_10, True)
    #if platform == "RF200":
    #    setRadioRate(3)
    #    rpc('\x00\x00\x02','logEvent','Radio Rate Set to 3')
    if (contactPortal):
        findPortal()        
@setHook(HOOK_1S)
def timer1SEvent(msTick):
    if portalAddr == '':
        findPortal()
    
def grnoff():
    writePin(greenLEDPin,True)
def grnon():
    writePin(greenLEDPin,False)
def redoff():
    writePin(redLEDPin,True)
def redon():
    writePin(redLEDPin,False)

def findPortal():
    """multicast to group 1 and no more than 3 hops away"""
    if (contactPortal):
        mcastRpc(1, 1, 'getPortal')
    return

def addressPortal():
    global portalAddr,portalConnected
    portalAddr = rpcSourceAddr()
    portalConnected = True
    redoff()
    grnon()
    pa = toHex(portalAddr)
    eventString = devName + " Recieved a reply from: " + pa + " while running " + str(imageName()) + " on a " + devType
    rpc(rpcSourceAddr(),'logEvent',eventString)
    return toHex(portalAddr)

    
@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    eventString = str(loadNvParam(8)) + ": " + str(pinNum) + " " + str(isSet)
    rpc(portalAddr,"logEvent",eventString)

"""###########################################################################"""
"""## from hexsupport2  ######################################################"""
"""###########################################################################"""
def hexNibble(nibble):
    '''Convert a numeric nibble 0x0-0xF to its ASCII string representation "0"-"F"'''
    hexStr = "0123456789ABCDEF"
    return hexStr[nibble & 0xF]

def hexNibble2(nibble):
    '''Convert a numeric nibble 0x0-0xF to its ASCII string representation "0"-"F"'''
    hexStr = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F"
    return hexStr[nibble & 0x0F]



def printHex(byte):
    '''print a byte in hex - input is an integer, not a string'''
    nib1 = hexNibble(byte >> 4)
    nib2 = hexNibble(byte)         # no trailing CR/LF
    hexStr = nib1 + nib2
    return hexStr

def printHexWord(word):
    '''print a word in hex - input is an integer, not a string'''
    printHex(word >> 8)
    printHex(word & 0xff)

def toHex(str):
    '''dump a string of bytes in hex'''
    hexstr = ''
    count = len(str)
    index = 0
    while index < count:
        hexstr += printHex(ord(str[index]))
        index += 1
    return hexstr
