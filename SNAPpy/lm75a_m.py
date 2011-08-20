"""
Program Description:    lm75a_m.py - Example I2C routines for the NXP LM75A Temp.
Uses the buildTWICmd from pcf2129a_m.py

CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

-------------------------------------------------------------------------------------------------
"""
LM75_ADDRESS = 72<<1    #slave aaddress is '1001'210, 2 1 0 are gnd =0. shifts to 10010000

def readLM75(firstReg, numRegs):
    """read registers starting at firstReg and numRegs"""
    cmd = buildTWICmd(LM75_ADDRESS, firstReg, False)
    #dumpHex(cmd)
    i2cWrite(cmd, retries, False)
    #print getI2cResult()
    
    cmd = chr( LM75_ADDRESS | 1 )
    #dumpHex(cmd)
    result = i2cRead(cmd, numRegs, retries, False)

    #dumpHex(result)
    return result

def shutdownLM75A():
    cmd = buildTWICmd(LM75_ADDRESS, 1, False)
    cmd += chr(1)
    #dumpHex(cmd)
    result = i2cWrite(cmd, retries, False)
    eventSting = "ShutdownLM75a: result:" + str(result) + " i2ccode:" + str(getI2cResult())
    #print eventSting
    return eventSting
def initLM75A():
    cmd = buildTWICmd(LM75_ADDRESS, 1, False)
    cmd += chr(0)
    #dumpHex(cmd)
    result = i2cWrite(cmd, retries, False)
    eventSting = "initLM75a: result:" + str(result) + " i2ccode:" + str(getI2cResult())
    #print eventSting
    return eventSting
    
def displayLMTemp():
    buffer = readLM75(0,2)
    t = (ord(buffer[0])) << 8 | ord(buffer[1])
    t = (t / 32) / 8
    #c =  t / 8
    return t
    
def displayLMTempF():
    t = displayLMTemp()
    t = (t * 9)/5 + 32
    return t