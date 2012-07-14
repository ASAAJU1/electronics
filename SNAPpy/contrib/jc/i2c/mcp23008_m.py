"""
Program Description:    mcp23008_m.py - Example I2C routines for the MCP23008 IO Expander.
Uses the buildTWICmd from pcf2129a_m.py

CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

201105281920    first version

-------------------------------------------------------------------------------------------------
"""
MCP23008_ADDRESS = 32<<1    #slave aaddress is '0100'210, 2 1 0 are gnd =0. shifts to 01000000

def _MCP23008Init():
    """Initialize MCP23008 and set defaults."""
    cmd = buildTWIcmd(MCP23008_ADDRESS, 0, False)
    cmd += chr(\xFF)
    x = 9
    while x > 0:
        cmd += chr('\x00')
        x -= 1
    result = i2cWrite(cmd, retries, False)
    return getI2cResult()

def _MCP23008_setPinDir(pin, dir):
    pass
