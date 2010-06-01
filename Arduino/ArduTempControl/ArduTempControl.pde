//#define DEBUG
//pin definitions
const int led_diag = 13;    //LED For Diagnostics
const int led_r = 11;		
const int led_g = 9;
const int led_b = 10;

const int RELAY_FAN = 6;	//G Relay on left
const int RELAY_HEAT = 7;	//W Relay in middle
const int RELAY_COOL = 8;	//Y Relay for cooling

const int IN_FAN = 12;		//G Input from existing thermostat
const int IN_HEAT = 4;		//W Input
const int IN_COOL = 5;		//Y Cool input from thermostat

int i=0;

float tempCurrent;
float tempSet = 72;

const int MIN_TIME = 60000;	// How long in ms between cycles.
                            // To prevent compressor problems, we never cycle the unit on and off quicker than this interval.
const int TEMP_STORE = 500;	// Where in the EEPROM we store the set temperature

long previousMillis = 1;
int interval = 1000;		//During Dev this has been reduced. 

void setup() {
	// initialize the digital pin as an output:
	//EEPROM_readAnything(0, configuration);

	pinMode(led_diag, OUTPUT);   
	pinMode(RELAY_FAN,OUTPUT);
	pinMode(RELAY_HEAT,OUTPUT);
	pinMode(RELAY_COOL,OUTPUT);  
	digitalWrite(RELAY_FAN,LOW);	//Ensure Relays are off
	digitalWrite(RELAY_HEAT,LOW);
	digitalWrite(RELAY_COOL,LOW);
	pinMode(IN_FAN,INPUT);			//Not needed, but 
	pinMode(IN_HEAT,INPUT);
	pinMode(IN_COOL,INPUT);

	// See if we can read the set temperature out of the EEPROM
	//byte gTemp = EEPROM.read(TEMP_STORE);
	//if (gTemp > 0) setTemp = (float)gTemp / 2; // Temperature is stored doubled

	Serial.begin(9600);
	Serial.println("ArduTempControl 20100529");	// Print identification and indicate end of setup

}

void loop() {
 if (millis() - previousMillis > interval || millis() < previousMillis) {
    // save the last time the loop ran
    previousMillis = millis();   
    if (Serial.available() > 0) {
      checkSerial();
    }
    //set_hvacmode(2);
    //return;
    
    if (digitalRead(IN_FAN) == HIGH) {
      if (digitalRead(IN_HEAT) == HIGH) {
        set_hvacmode(1);
      } else if (digitalRead(IN_COOL) == HIGH) {
        set_hvacmode(2);
      } else {
        set_hvacmode(3);
      }
    } else {
      set_hvacmode(0);
    }
 
    
    
    
    
  } else { //too early for main loop
    if (Serial.available() > 0) {
      checkSerial();
    }
  } // close the else to the main if time check
  
}

int checkSerial() {
  
}

void set_hvacmode(int hvacmode) {
	switch (hvacmode) {
		case 0:    // all OFF
		digitalWrite(RELAY_FAN,LOW);
		digitalWrite(RELAY_HEAT,LOW);
		digitalWrite(RELAY_COOL,LOW);
		analogWrite(led_g, 255);
		analogWrite(led_r, 255);
		analogWrite(led_b, 255);
		#ifdef DEBUG
			Serial.println("hvacmode 0");
		#endif
		break;
		case 1:  // Heat + Fan
		digitalWrite(RELAY_FAN,HIGH);
		digitalWrite(RELAY_HEAT,HIGH);
		digitalWrite(RELAY_COOL,LOW);
		analogWrite(led_g, 255);
		analogWrite(led_r, 0);
		analogWrite(led_b, 255);
		break;
		case 2:  // COOL + FAN
		digitalWrite(RELAY_FAN,HIGH);
		digitalWrite(RELAY_HEAT,LOW);
		digitalWrite(RELAY_COOL,HIGH);
		analogWrite(led_g, 255);
		analogWrite(led_r, 255);
		analogWrite(led_b, 0);
		break;
		case 3:  // FAN Only
		digitalWrite(RELAY_FAN,HIGH);
		digitalWrite(RELAY_HEAT,LOW);
		digitalWrite(RELAY_COOL,LOW);
		analogWrite(led_g, 0);
		analogWrite(led_r, 255);
		analogWrite(led_b, 255);
		break;
		default:  // Any other condition. For safety this is the same as 0
		digitalWrite(RELAY_FAN,LOW);
		digitalWrite(RELAY_HEAT,LOW);
		digitalWrite(RELAY_COOL,LOW);
		analogWrite(led_g, 255);
		analogWrite(led_r, 255);
		analogWrite(led_b, 255);
	}
    
}
