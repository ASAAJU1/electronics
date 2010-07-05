// ArduTemp remote boards.
// Send temperature
// goto sleep for 60 seconds
// send report, check for queued commands

#include <Wire.h>
#include <EEPROM.h>
int node; 
const int NODE_STORE = 500;
byte nodeValue;

int i;
byte res;
byte msb;
byte lsb;
int val;
float valF;
int valP;

void setup()
{
  nodeValue = EEPROM.read(NODE_STORE);
  node = int(nodeValue);
  Serial.begin(9600);
  Serial.println("ArduTempSender version 2010.07.04");
  Serial.println(nodeValue);
  Serial.println(node);
  
  Wire.begin();
  i = 0;
  //Serial.println("End Setup.");
}

void loop()
{
res = Wire.requestFrom(72,2); //add0 tied to GND
if (res == 2) {
  msb = Wire.receive(); /* Whole degrees */
  lsb = Wire.receive(); /* Fractional degrees */
  //Serial.print(msb,BIN);
  //Serial.print(".");
  //Serial.print(lsb,BIN);
  val = ((msb) << 4) | ((lsb) >> 4); /* LSB */
  valF = (val*0.1125+32);
  valP = val*0.0625;
  printvalb();

  delay(1000);
  }
  //Serial.print(".");
}

void printvalb(void) {
  Serial.print(valP,BYTE);
}

void printvalf(void) {
  Serial.print( readVcc(), DEC );
  Serial.print(": ");
  Serial.print( millis(), DEC );
  Serial.print(": ");
  Serial.print(valF);
  Serial.print(": ");
  //Serial.print(val,BYTE);
  Serial.println(valP,BYTE);
}

void phoneHome(int id, int val) {
 Serial.print("@|");
 Serial.print(id);
 Serial.print("|");
 Serial.print(val);
 Serial.print("|");
 Serial.print(millis());
 Serial.println("|#\r");
 delay(1000);
 if (Serial.available() >0) {
   //
 }
  
}

long readVcc() {
  long result;
  // Read 1.1V reference against AVcc
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Convert
  while (bit_is_set(ADCSRA,ADSC));
  result = ADCL;
  result |= ADCH<<8;
  result = 1126400L / result; // Back-calculate AVcc in mV
  return result;
}
