"""
CC BY 3.0  J.C. Woltz
http://creativecommons.org/licenses/by/3.0/

import as module. just quick common functions between scrtips. 
jc_cnc_m.py
JC Command and Control Module and Helper functions CNC expects

Modified 201112291302 to sect all contact disabled. Added Enable/Disable for E10,Portal,SnapConect
                      also changed the name of addressPortal to match other scripts.
"""
contactPortal = False
contactE10    = False
contactSC     = False

def findPortal():
    """multicast to group 1 and no more than 4 hops away"""
    if (contactPortal):
        mcastRpc(1, 4, 'getPortal')
    return
def addressPortal():
    """Set the portal SNAP address to the caller of this function"""
    global portalAddr
    portalAddr = rpcSourceAddr()
    #getPortalTime()
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

def contactSCEnable():
    global contactSC
    contactSC = True
def contactSCDisable():
    global contactSC
    contactSC = False
def contactE10Enable():
    global contactE10
    contactE10 = True
def contactSCDisable():
    global contactE10
    contactE10 = False

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