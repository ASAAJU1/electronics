"""
Example of using two SNAP Pro wireless nodes to replace a RS-232 cable
Edit this script to specify the OTHER node's address, and load it into a node
Node addresses are the last three bytes of the MAC address
MAC Addresses can be read off of the RF Engine sticker
For example, a node with MAC Address 001C2C1E 86001B67 is address 001B67
In SNAPpy format this would be address "\x00\x1B\x67"
"""
from synapse.switchboard import *
from synapse.platforms import *

otherNodeAddr = "\x00\x65\x1D" # <= put the address of the OTHER node here
#this is the computer side node
ASetReset = GPIO_10
AResetPin = GPIO_9


@setHook(HOOK_STARTUP)
def startupEvent():
    #Set NV Parameters for reliable serial
    NeedRestart=SetParam(13, 0, NeedRestart)
    NeedRestart=SetParam(14, 110, NeedRestart)
    NeedRestart=SetParam(15, 5, NeedRestart)
    
    if NeedRestart:
        reboot()
    
    initUart(1, 57600) # <= put your desired baudrate here!
    flowControl(1, False) # <= set flow control to True or False based on the needs of your application
    crossConnect(DS_UART1, DS_TRANSPARENT)
    ucastSerial(otherNodeAddr)
    setPinDir(ASetReset, False)   #Input
    monitorPin(ASetReset, True)   #monitor changes to this pin. 
    setRate(3)  #1 ms monitoring of pin


def SetParam(ID, Value, Pass):
    """code from reblli1 to set NV Parameters if different"""
    if loadNvParam(ID) != Value:
        saveNvParam(ID, Value)
        return True
    else:
        return Pass
    
    
@setHook(HOOK_GPIN)
def buttonEvent(pinNum, isSet):
    """Hooked into the HOOK_GPIN event"""
    #mostly debug and pointless irw
    if (pinNum == ASetReset):
        if (isSet == False):
            rpc(otherNodeAddr, "writePin", AResetPin, False)
        else:
            rpc(otherNodeAddr, "writePin", AResetPin, True)
    
def resetArduino():
    #writePin(AResetPin, False)
    #writePin(AResetPin, True)
    pulsePin(AResetPin, 40, False)