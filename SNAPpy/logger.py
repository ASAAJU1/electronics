
portalAddress = '\x00\x00\x01'


def log(txt):
    rpc(portalAddr, "logEvent", txt)   
    
def setPortalAddress(addressByteStr):
    global portalAddress
    portalAddress = addressByteStr
    
    