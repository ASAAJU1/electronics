"""
CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

import as module. just quick common functions between scrtips. 
jc_cnc_m.py
JC Command and Control Module and Helper functions CNC expects
"""
contactPortal = True
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
def contactportalDisable():
    global contactPortal
    contactPortal = False
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