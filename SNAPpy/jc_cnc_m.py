"""
CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

import as module. just quick common functions between scrtips. 
jc_cnc_m.py
JC Command and Control Module and Helper functions CNC expects
"""
contactPortal = False
contactE10 = False
allowSleep = True

def set_portal_addr():
    """Set the portal SNAP address to the caller of this function"""
    global portalAddr
    portalAddr = rpcSourceAddr()
    getPortalTime()
def contactSCEnable():
    global contactSC
    contactSC = True
def contactSCDisable():
    global contactSC
    contactSC = False
def contactportalEnable():
    global contactPortal
    contactPortal = True
    rpc(portalAddr, "logEvent", "Contact Portal Enabled")
    return 1
def contactportalDisable():
    global contactPortal
    contactPortal = False
    rpc(portalAddr, "logEvent", "Contact Portal Disenabled")
    return 0
def allowSleepEnable():
    global allowSleep
    allowSleep = True
def allowSleepDisable():
    global allowSleep
    allowSleep = False  
def resetClock():
    global timeSynced
    timeSynced = False
def csleep(a,b):
    sleep(int(a),int(b))