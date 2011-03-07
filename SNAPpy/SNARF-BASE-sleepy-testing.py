"""
Script for remote data node of sleepy mesh. Uses functions from sleepyTemplate.py
"""


# Use Synapse Evaluation Board definitions

from sleepyTemplate import *
from synapse.platforms import *
from synapse.switchboard import *
from synapse.pinWakeup import *
from pcf2129a_m import *
from lm75a_m import *
from m24lc256_m import *

portalAddr = '\x00\x00\x01' # hard-coded address for Portal <------------<<<<<<<<
secondCounter = 0 
minuteCounter = 0
datablock = 1
taddress = 64

MCLR_PIN = GPIO_13
REQ_PIN = GPIO_11
SLEEP_PIN = GPIO_12

VAUX = GPIO_5
RTC_INT = GPIO_10


STATE_NULL = 0
STATE_PACKET = 1
STATE_STRING = 2
MAX_STRING = 32

stdioState = STATE_NULL

homeAddr = ''
lastRecCnt = 0
forwardStr = ''


def atStartup():

    global stdioState  
    global lastRecCnt
    global recCnt
    global forwardStr
        
    
    
    #configure unused pins for low power
    setPinDir(GPIO_0,False)   #input
    setPinPullup(GPIO_0,True) #enable pullup
    setPinDir(GPIO_1,False)   #input
    setPinPullup(GPIO_1,True) #enable pullup
    setPinDir(GPIO_2,False)   #input
    setPinPullup(GPIO_2,True) #enable pullup
    setPinDir(GPIO_3,False)   #input
    setPinPullup(GPIO_3,True) #enable pullup
    setPinDir(GPIO_5,True)   #outout
    writePin(VAUX, False)
    setPinDir(GPIO_6,False)   #input
    setPinPullup(GPIO_6,True) #enable pullup
    setPinDir(GPIO_14,False)   #input
    setPinPullup(GPIO_14,True) #enable pullup
    setPinDir(GPIO_15,False)   #input
    setPinPullup(GPIO_15,True) #enable pullup
    setPinDir(GPIO_16,False)   #input
    setPinPullup(GPIO_16,True) #enable pullup
    #setPinDir(GPIO_17,False)   #input
    #setPinPullup(GPIO_17,True) #enable pullup 
    #setPinDir(GPIO_18,False)   #input
    #setPinPullup(GPIO_18,True) #enable pullup 
   
   
    lastRecCnt = 0
    recCnt = 0
    forwardStr = ''
    stdioState = STATE_NULL
    
    i2cInit(True)
    
    setPinDir(MCLR_PIN, False)  #input 
    writePin(MCLR_PIN,True)    #set high for when configured as output   
    setPinDir(REQ_PIN,False)   #input tied to PIC24 for general use, not currently used
    setPinPullup(REQ_PIN,True) #pullup
        
    setPinDir(SLEEP_PIN, True)  #output
    writePin(SLEEP_PIN,True)   #set high, want to jump to app
     
    initUart(1,9600)
    flowControl(1,False)     # no flow control
    stdinMode(1,False)       #char mode (not line mode), no echo
    crossConnect(DS_UART1,DS_STDIO)
    
    checkClockYear()
    
  
def beforeSleep(duration):
    """This helper routine is invoked right before going to sleep"""
    wakeupOn(RTC_INT, True, False)
    buff = readPCF2129(0x03,2)
    
    Seconds = bcdToDec(ord(buff[0]) & 0x7F)
    Minutes = bcdToDec(ord(buff[1]) & 0x7F)
    
    writeClockAlarm(00,00)
    writePin(SLEEP_PIN,False)   #tell micro to go to sleep
    writePin(VAUX, False)       #turn off auxilary regulator


def afterSleep():
    """This helper routine is invoked right after waking up"""
    writePin(SLEEP_PIN,True)   #tell micro to wakeup
    doMCLR()                   #sleep pin high causes bootloader firmware to skip timer sequence
    #toggling MCLR assures that we get processor attention, even if it is hung by software error
    global datablock
    #address = datablock * 64
    global taddress
    
    eventString = str(displayClockDT()) + "," + str(displayLMTemp()) + "," + str(displayLMTempF()) + ",EOB"
    t = len(eventString)
    if (t < 32):
        index = t
        while (index < 32):
            eventString = eventString + "0"
            index += 1
    tt = len(eventString)
    writeEEblock(taddress, eventString)

    eventString = eventString + " " + str(t) + " " + str(taddress) + " " + str(tt)
    rpc(portalAddr, "logEvent", eventString)
    #if (t < 32):
    #    t = 32
    taddress += tt
    datablock += 1
    
    #return getI2cResult()


def every100ms():
    """This helper routine is invoked every 100 milliseconds while awake"""
    pass


def everySecond():
    """This helper routine is invoked every second while awake"""
    pass
    eventString = str(displayLMTempF()) + "," + str(displayLMTemp())
    print eventString
    print displayClockDT()
    

def showElection():
    """Show that an election is currently in progress
       This helper routine is just for demo purposes"""
    pass


def showLeadership(isLeader):
    """Show if this node is (or is not) the leader
       This helper routine is just for demo purposes"""

    pass

def monitorMeshUp():
    pass


def doMCLR():
    setPinDir(MCLR_PIN, True)  #output
    writePin(MCLR_PIN,True)
    writePin(MCLR_PIN,False)
    writePin(MCLR_PIN,True)
    setPinDir(MCLR_PIN, False)  #input 
 
 
## DO NOT CHANGE THIS FUNCTION NAME, C CODE depends on it.
def doUcReset():
    global homeAddr
    homeAddr = rpcSourceAddr()
    writePin(SLEEP_PIN,False)   #set low to force bootloader firmware through normal sequence
    doMCLR()


def outString(s):
    global homeAddr
    homeAddr = rpcSourceAddr() #must remember who called us!
    print s,
 
    
@setHook(HOOK_STDIN)
def stdinEvent(buf):
    """Receive handler for character input on UART0.
       The parameter 'buf' will contain one or more received characters. 
    """
    global forwardStr
    global recCnt
    global packetLen
    global stdioState
  
    n = len(buf)
    i = 0
    while (i < n):
        if (stdioState == STATE_NULL):
            if (ord(buf[i]) == 0x1E):
                #check if entire packet is in buffer
                if ((i == 0) and (n > 2) and (n-2) == ord(buf[1])):
                    #entire packet here, send it.
                    forwardStr = buf[i]
                    forwardStr += localAddr() # insert our address
                    forwardStr += buf[1:] 
                    rpc(homeAddr,'outString',forwardStr)
                    forwardStr = ''  
                    return
                else:
                    #have to accumulate the packet
                    forwardStr = buf[i]
                    forwardStr += localAddr()
                    recCnt = 1
                    stdioState = STATE_PACKET
        elif (stdioState == STATE_PACKET):
            #accumulating a packet
            forwardStr += buf[i]
            recCnt += 1      
            if (recCnt == 2):
                 packetLen = ord(buf[i])               
            elif (recCnt > 2):
                if ((recCnt-2) == packetLen):
                    recCnt = 0
                    #we are done, forward to node
                    stdioState = STATE_NULL
                    rpc(homeAddr,'outString',forwardStr)
                    forwardStr = ''
                    return
                    
   
        i += 1
 
# hook up event handlers
snappyGen.setHook(SnapConstants.HOOK_STARTUP, startupEvent)
snappyGen.setHook(SnapConstants.HOOK_100MS, timer100msEvent)
snappyGen.setHook(SnapConstants.HOOK_RPC_SENT, rpcsentEvent)
    
            
