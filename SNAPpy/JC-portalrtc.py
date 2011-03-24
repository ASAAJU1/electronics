"""
J.C. Woltz's Portal Script. 
setRFTime function written by me.

get_temp_logger written by Synapse Wireless

"""


import binascii
import time

#import thermistor


CSV_FILENAME = "tempDataLog.csv"

def setRFTime(nodeAddr):
    """Call with nodeAddr to set the time on that node"""
    Year = int(time.strftime('%y'))
    Month = int(time.strftime('%m'))
    Date = int(time.strftime('%d'))
    Hour = int(time.strftime('%H'))
    Minute = int(time.strftime('%M'))
    Second = int(time.strftime('%S'))
    DOW = int(time.strftime('%w'))
    
    rpc(nodeAddr, "writeClockTime", Year, Month, Date, DOW, Hour, Minute, Second)
    
def setRFPCF2129Time():
    """Call with nodeAddr to set the time on that node"""
    Year = int(time.strftime('%y'))
    Month = int(time.strftime('%m'))
    Date = int(time.strftime('%d'))
    Hour = int(time.strftime('%H'))
    Minute = int(time.strftime('%M'))
    Second = int(time.strftime('%S'))
    DOW = int(time.strftime('%w'))
    
    mcastrpc(1, 3, 'writeClockTime', Year, Month, Date, DOW, Hour, Minute, Second)
    
###############################################################################
## Below is from Synapse Wireless    ##########################################
###############################################################################
def plotlq(who, lq): 
  logData(who,lq,256)

#Thermistor characteristics based on thermistor type used
BETA = 4450.0      # K
R25 = 100000.0  # Ohms
PULLUP_RESISTOR = 100000.0

ADC_FULLSCALE = 1023


def report_temp(temp_val):
    global prev_temp

    tempK = thermistor.ntcTherm(adc_to_resistance(temp_val), BETA, R25)
    tempF = thermistor.fahrenheit(tempK)

    #Format the current time to something Excel can use
    row = '%s,%s,%i\r\n' % (time.strftime('%m/%d/%Y %H:%M:%S'), 
                            binascii.hexlify(remoteAddr), 
                            tempF)
    csv = open(CSV_FILENAME, 'a')
    csv.write(row)
    csv.close()

def get_portal_logger():
    rpc(remoteAddr, "set_portal_addr", Portal.netAddr)

def adc_to_resistance(adc_val):
    return PULLUP_RESISTOR * adc_val / (ADC_FULLSCALE - adc_val)
