"""
Example of using two SNAP Pro wireless nodes to replace a RS-232 cable
Edit this script to specify the OTHER node's address, and load it into a node
Node addresses are the last three bytes of the MAC address
MAC Addresses can be read off of the RF Engine sticker
For example, a node with MAC Address 001C2C1E 86001B67 is address 001B67
In SNAPpy format this would be address "\x00\x1B\x67"
"""
from synapse.switchboard import *

otherNodeAddr = "\x00\x65\x21" # <= put the address of the OTHER node here

def startupEvent():
    initUart(1, 57600) # <= put your desired baudrate here!
    flowControl(1, False) # <= set flow control to True or False based on the needs of your application
    crossConnect(DS_UART1, DS_TRANSPARENT)
    ucastSerial(otherNodeAddr)

snappyGen.setHook(SnapConstants.HOOK_STARTUP, startupEvent)
