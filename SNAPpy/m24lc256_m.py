"""
CAT24C128.py - Example routines for the Catalyst Semiconductor 128 Kb Serial EEPROM

This chip is arranged as 16384 words of 8 bits each. It has three address lines,
allowing up to eight of them to share a single I2C bus.

Note that the focus of this script was to demonstrate the new I2C capabilities
of SNAP 2.1, not to exercise every feature of the EEPROM chip. Please refer to
the CAT24C128 data sheet to see what else it is capable of.

NOTE! - This script requires SNAP 2.1 or greater! It uses the I2C support first
added in SNAP 2.1, and will not work in a SNAP 2.0 node.

------------------------------------------------------------------------------
modified for 24LC256 with address lines tied to GND. 
To be imported as module
"""

from synapse.hexSupport import *
EEPROM_ADDRESS = 80 << 1 


def readEEPROM(memoryAddress, dataLen):
    if dataLen > 63: # SNAPpy limitation, not I2C or EEPROM limitation
        print "too much data being read at once"
        return ""

    if memoryAddress >= 0x8000:
        print "invalid memory address - chip only holds 32K"
        return ""
    
    cmd = ""
    cmd += chr( EEPROM_ADDRESS )
    
    #cmd = buildPrefix(chipAddress, False) # we have to WRITE the address we want to read

    # Add desired memory address onto the prefix string just built
    cmd += chr( memoryAddress >> 8 )
    cmd += chr( memoryAddress & 0xff)

    #dumpHex(cmd)

    result = i2cWrite(cmd, retries, False)
    #print "Read Select address result: "
    #print result

    cmd = chr( EEPROM_ADDRESS | 1 ) # NOW we can read data back

    result = i2cRead(cmd, dataLen, retries, False)
    #print getI2cResult()
    return result

# Gotchas:
# 1) Can only write within a page in a single command
# 2) Can only write a page at a time
# 3) SNAPpy dynamic string limitations limit this further
def writeEEblock(memoryAddress, data):
    if len(data) > 61:
        print "too much data being written at once" # SNAPpy limitation
        return

    if memoryAddress >= 0x8000:
        print "invalid memory address - chip only holds 32K"
        return

    cmd = chr( EEPROM_ADDRESS ) # NOT a read

    # Add desired memory address onto the prefix string just built
    cmd += chr( memoryAddress >> 8 )
    cmd += chr( memoryAddress & 0xff)

    # Add on the actual data bytes
    cmd += data

    #dumpHex(cmd)

    i2cWrite(cmd, retries, False)
    
def eraseEEProm():
    String2 = ""
    index = 0
    jc = 0
    while (index < 60):
        String2 = String2 + "0"
        index += 1
    print String2
    index = 0
    while (index < 512):
        print str(index)
        ttaddress = index * 64
        print ttaddress
        writeEEblock(ttaddress,String2)
        index += 1
        cmd = chr( EEPROM_ADDRESS ) # NOT a read
        print "Start waiting for ack"
        while (jc <> 1):
            jc = 0
            i2cWrite(cmd, retries, False)
            tt = getI2cResult()
            print tt
            jc = tt
                
                
            
        