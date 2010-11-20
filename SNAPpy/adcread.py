"""
  Charging Base Demo version 1

"""

from synapse.platforms import *
from synapse.switchboard import *

#ADR510
adrRead = GPIO_18
adrReadADC = 0
#Two 1 MegaOhm Resistors to monitor battery
vDiv = GPIO_17
vDivADC = 1
#MAX6520 to compare against ADR510
max6520 = GPIO_16
max6520ADC = 2

mcStat1 = GPIO_10
mcStat2 = GPIO_9
vRegAux = GPIO_2
adrPower = GPIO_1

battThreshold = 33
secondCounter = 0

@setHook(HOOK_STARTUP)
def startupEvent():
    """This is hooked into the HOOK_STARTUP event"""
    setPinDir(adrPower, True)   #output
    writePin(adrPower, False)   #turn off
    setPinDir(vRegAux, True)    #output
    writePin(vRegAux, False)    #turn off
    
    setPinDir(mcStat1, False)   #input
    setPinDir(mcStat2, False)   #input
    initUart(0, 9600)
    crossConnect(DS_STDIO,DS_UART0)
    
def powerUpVoltageMonitor():
    """Power up the voltage monitoring circuit"""
    writePin(adrPower, True)

def powerDownVoltageMonitor():
    """Power down the circuit. Reported values are bogus"""
    writePin(adrPower, False)

def powerUpAuxVoltageR():
    """Power up the aux voltage regulator circuit"""
    writePin(vRegAux, True)

def powerDownAuxVoltageR():
    """Power down the aux voltage regulator circuit"""
    writePin(vRegAux, False)

def readVCC():
    """returns VCC voltage in .1 volt increments, assuming circuit is powered"""
    powerUpVoltageMonitor()
    refAdc = readAdc(adrReadADC)
    powerDownVoltageMonitor()
    vcc = (10240 / refAdc) + 1 # + 1 to compensate for truncation effects
    print vcc
    return vcc

def readBatt():
    """returns Battery level from ADC"""
    vdivref = readAdc(vDivADC)
    batt = vdivref * (readVCC() * 100/1024) * 3
    return batt 

def setThreshold(newThreshold):
    """Change the threshold at which the alarm sounds"""
    global battThreshold
    battThreshold = newThreshold

def sensorUpdate():
    """Read the temperature from the sensor"""
    global battThreshold
    
    vcc = readVCC()
    
    #adcValue0 = readAdc(0) # Check the temperature
    #adcValue1 = readAdc(1) # Check the temperature
    #adcValue2 = readAdc(2) # Check the temperature
    #adcValue3 = readAdc(3) # Check the temperature
    #print "0:",adcValue0," 1:", adcValue1," 2:", adcValue2," 3:", adcValue3 #DEBUG
 
    if vcc < battThreshold: # If temp is over the limit (below the raw value)..., 
        print "Vcc at: ", vcc
        beginCountdown() #...start the countdown to the alarm

def soundTheAlarm():
    """Activate the buzzer"""
    global countdown, buzzerPin
    print "Sound the Alarm" #DEBUG
    countdown = False
    #writePin(greenLedPin, False) # Turn off the green LED
    mcastRpc(1,2,"soundTheAlarm")
    #pulsePin(buzzerPin, 1500, True)

def beginCountdown():
    """Begin a 5 second countdown that will lead to the alarm sounding"""
    global countdown, alarmCounter, greenLedPin
    if not countdown: # Don't restart things if it has already triggered
        print "Begin Countdown" #DEBUG
        #blinkLed(1000) # Flash yellow LED
        #writePin(greenLedPin, True) # Light the green LED
        mcastRpc(1,2,"beginCountdown") # Tell any  other nodes
        countdown = True
        alarmCounter = 0
    
def alarmCutOff():
    """Disable the alarm before it goes off"""
    global countdown, alarmCounter
    #writePin(greenLedPin, False) # Turn off the green LED    

    # Report to remote nodes that that the buzzer unit has seen the alarmCutOff
    mcastRpc(1,2,"alarmCutOffRequested")
    
    #pulsePin(buzzerPin, 20, True) # Chirp the local buzzer
    countdown = False
    alarmCounter = 0

def doEverySecond():
    """Things to be done every second"""    
    global alarmCounter, countdown
    #blinkLed(200)
    sensorUpdate()
    if countdown:
        alarmCounter += 1
        print "Alarm Count= ", alarmCounter #DEBUG
        if alarmCounter >= 5:
            soundTheAlarm()

@setHook(HOOK_100MS)
def timer100msEvent(msTick):
    """Hooked into the HOOK_100MS event"""
    global secondCounter
    secondCounter += 1
    if secondCounter >= 10:
        doEverySecond()      
        secondCounter = 0
        #batteryX10 = readVCC()
        #print 'VCC=',batteryX10 / 10,'.',batteryX10 % 10