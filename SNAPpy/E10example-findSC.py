"""
E10example.py - just an example for a SNAP Engine running INSIDE an E10
E10example-findSC.py - modified to include functions to locate the E10 or
                       snap connect the node is directly connected to.
"""
from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *

# The SNAP Engine controls an LED labeled "A" on the "wireless" end of the unit
# (next to the MODE button)
LED_A_GREEN = GPIO_0
LED_A_RED = GPIO_1

# misc counters
secondCounter = 0
minuteCounter = 0
msCounter = 0

# various bool values to track when we establish certain connections
e10connected    = False
portalConnected = False
contactPortal   = True
e10Contacted    = False
portalContacted = False

#Setup global vars for addresses
portalAddr      = ''
snapConnectAddr = ''

@setHook(HOOK_STARTUP)
def startup():
    setPinDir(LED_A_GREEN, True)
    setPinDir(LED_A_RED, True)
    setLedAYellow()
    findSnapConnect()
    if (contactPortal):
        findPortal()
    #if platform == "RF200":
    #    setRadioRate(3)

    
@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global secondCounter, minuteCounter
    secondCounter += 1
    if snapConnectAddr == '':
        #Always search for snap connect if we have no address. The address should
        #not change without the node rebooting.
        findSnapConnect()
        return  #by returning without snapConnectAddr, the rest of this does not run
    if (e10connected == False):
        setLedARed()
        #rpc(portalAddr, "logEvent", secondCounter %10)
        if (secondCounter % 10 == 0):
            #switchUART1()
            pingSnap()
        return
    if e10connected == True:
        setLedAGreen()
    if secondCounter >= 600:
        secondCounter -= 600
        minuteCounter += 1
        pingSnap()
        #checkPending()

def setLedAOff():
    writePin(LED_A_GREEN, False)
    writePin(LED_A_RED, False)

def setLedAGreen():
    writePin(LED_A_GREEN, True)
    writePin(LED_A_RED, False)

def setLedARed():
    writePin(LED_A_GREEN, False)
    writePin(LED_A_RED, True)

def setLedAYellow():
    writePin(LED_A_GREEN, True)
    writePin(LED_A_RED, True)
    #writePin(LED_A_ORANGE, True)
    
def echo(msg):
    print str(msg)

def pingSnap():
    global e10connected
    e10connected = False
    rpc(snapConnectAddr, "pingSnap")
    if (portalConnected):
        rpc(portalAddr, "logEvent", loadNvParam(8) + ": pingSnap : ping " + toHex(str(snapConnectAddr)))
def pongSnap():
    global e10connected
    e10connected = True
    rpc(rpcSourceAddr(),'logToSQL',str(loadNvParam(8)),"Reply from Snap Connect")
    if (portalConnected):
        rpc(portalAddr, "logEvent", loadNvParam(8) + ": pongSnap: pong " + toHex(str(rpcSourceAddr())))

def findPortal():
    """multicast to group 1 and no more than 3 hops away"""
    if (contactPortal):
        mcastRpc(1, 3, 'whereIsPortal',str(loadNvParam(8)),str(getNetId()),imageName())
    return

def setPortalAddr():
    global portalAddr,portalConnected,portalContacted
    portalAddr = rpcSourceAddr()
    portalConnected = True
    portalContacted = True
    #rpc(portalAddr,'logEvent',"Hello Portal")
    return str(toHex(str(portalAddr)))
    
"""###########################################################################"""
"""### Function form Bruce (BSB) 201108230014   ##############################"""
"""###########################################################################"""
def findSnapConnect():
    """Look for snap conect that we are directly connected to"""
    return mcastRpc(1,1,'whereIsSnap',str(loadNvParam(8)),str(getNetId()),imageName())
    #Sending snap connect the node name, full netid, scriptname
def setSnapConnectAddr():
    global snapConnectAddr
    snapConnectAddr = rpcSourceAddr()
    if (portalConnected):
        eventString = str(loadNvParam(8)) + ": snapConnectReply: " + toHex(str(snapConnectAddr))
        rpc(portalAddr,"logEvent",eventString)
    
"""###########################################################################"""
"""### Function from http://forums.synapse-wireless.com/showthread.php?t=688 #"""
"""###########################################################################"""


@setHook(HOOK_RPC_SENT)
def checkPending():
    pass
#    global pendingNodes,i,dataSkip
#    if len(checkPending) >= 3:
#        if rpc(pendingNodes[0:3], 'bar'):
#            pendingNodes = pendingNodes[3:]
#    if dataSkip == False and i > 0:
#        if (rpc(snapConnectAddr,"logToBSB",str(i),"abcdef")):
#            i -= 1
#    else:
#        dataSkip = True
# Some function that multiple remote nodes might call in a burst,
# that requires an answer in return
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
