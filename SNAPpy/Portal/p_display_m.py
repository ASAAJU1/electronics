def dispayLastWriteAddress(tt):
    remoteNode.setColumn("Next EEPROM Address", tt)
    
def WakeAlert(Minutes, Seconds):
    eventString = str(Minutes) + " " + str(Seconds)
    remoteNode.setColumn("Wake At",eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def WakeDisplay(Years, Months, Days, DOW, Hours, Minutes, Seconds):
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    eventString = str(displayDOW(DOW)) + " " + str(20) + str(Years) + "." + str(Months) + "." + str(Days) + " " + str(Hours) + ":" +  str(Minutes) + ":" + str(Seconds)
    remoteNode.setColumn("Wake At",eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def GClockDisplay(Column, Years, Months, Days, DOW, Hours, Minutes, Seconds):
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    eventString = str(displayDOW(DOW)) + " " + str(20) + str(Years) + "." + str(Months) + "." + str(Days) + " " + str(Hours) + ":" +  str(Minutes) + ":" + str(Seconds)
    remoteNode.setColumn(Column,eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def LastReadDisplay(Years, Months, Days, DOW, Hours, Minutes, Seconds):
    
    if (Months < 10):
        Months = str(0) + str(Months)
    if (Days < 10):
        Days = str(0) + str(Days)
    if (Hours < 10):
        Hours = str(0) + str(Hours)
    if (Minutes < 10):
        Minutes = str(0) + str(Minutes)    
    if (Seconds < 10):
        Seconds = str(0) + str(Seconds)
    eventString = str(displayDOW(DOW)) + " " + str(20) + str(Years) + "." + str(Months) + "." + str(Days) + " " + str(Hours) + ":" +  str(Minutes) + ":" + str(Seconds)
    remoteNode.setColumn("LastRead At",eventString)
    #rpc(remoteAddr, "portalcmdsleep")

def graph_generic(who, data):
    remoteNode.setColumn(who, data)
    logData(who, data)
    logToCSV(who, str(data))

def graph_generic_lqdts(who, data, lq, dts): 
    if who == None:
        who = convertAddr(remoteAddr)
    whoLQ = str(who) + "-LQ"
    logData(whoLQ,lq,128)
    logData(who, data)
    logToCSV(who, str(data))
    remoteNode.setColumn("Link", lq)
    remoteNode.setColumn("DT", dts)
