//#define F_CPU 8000000UL
//#define F_CLOCK 8000000UL
// A simple data logger for the Arduino analog pins
#define LOG_INTERVAL  200 // mills between entries
#define ECHO_TO_SERIAL   1 // echo data to serial port
#define WAIT_TO_START    0 // Wait for serial input in setup()
#define SYNC_INTERVAL 1000 // mills between calls to sync()
uint32_t syncTime = 0;     // time of last sync()

// This line defines a "Uart" object to access the serial port
HardwareSerial Uart = HardwareSerial();

#include <SdFat.h>
#include <SdFatUtil.h>
#include <Wire.h>

Sd2Card card;
SdVolume volume;
SdFile root;
SdFile file;

char inByte;

int led3 = 24;
int led4 = 9;
int ledr = 4;
int ledg = 14;
int ledb = 15;
int ledblevel = 0;

int powersave = 0;
int ledson = 1;

// store error strings in flash to save RAM
#define error(s) error_P(PSTR(s))

void error_P(const char* str) {
  digitalWrite(ledr,HIGH);
  PgmPrint("error: ");
  SerialPrintln_P(str);
  if (card.errorCode()) {
    PgmPrint("SD error: ");
    Serial.print(card.errorCode(), HEX);
    Serial.print(',');
    Serial.println(card.errorData(), HEX);
    Uart.print("error: ");
    Uart.print(str);
    Uart.print(",");
    Uart.print(card.errorCode(), HEX);
    Uart.print(',');
    Uart.println(card.errorData(), HEX);
  }
  while(1){
    digitalWrite(ledr,LOW);
    delay(500);
    digitalWrite(ledr,HIGH);
    delay(500);
    PgmPrint("SD error: ");
    Serial.print(card.errorCode(), HEX);
    Serial.print(',');
    Serial.println(card.errorData(), HEX);
  }
}

void setup(void) {
  Uart.begin(9600);
  pinMode(led4,OUTPUT);
  digitalWrite(led4, HIGH);
  //DDRD &= ~((0<<0) | (0<<1));
  //PORTD |= (1<<0) | (1<<1);
  Wire.begin(0x50);                // join i2c bus with address #2
  Wire.onRequest(requestEvent); // register event
  Serial.begin(9600);
  Serial.println();
  pinMode(led3,OUTPUT);
  pinMode(led4,OUTPUT);
  pinMode(ledr,OUTPUT);
  pinMode(ledg,OUTPUT);
  pinMode(ledb,OUTPUT);
  //digitalWrite(led4, HIGH);
  
  

  
#if WAIT_TO_START
  Serial.println("Type any character to start");
  while (!Serial.available());
#endif //WAIT_TO_START

  // initialize the SD card at SPI_HALF_SPEED to avoid bus errors with
  // breadboards.  use SPI_FULL_SPEED for better performance.
  if (!card.init(SPI_HALF_SPEED)) error("card.init failed");
  
  // initialize a FAT volume
  if (!volume.init(&card)) error("volume.init failed");
  
  // open root directory
  if (!root.openRoot(&volume)) error("openRoot failed");
  
  // create a new file
  char name[] = "LOGGRR00.CSV";
  for (uint8_t i = 0; i < 100; i++) {
    name[6] = i/10 + '0';
    name[7] = i%10 + '0';
    if (file.open(&root, name, O_CREAT | O_EXCL | O_WRITE)) break;
  }
  if (!file.isOpen()) error ("file.create");
  Serial.print("Logging to: ");
  Serial.println(name);
  Uart.print("Filename: ");
  Uart.println(name);


  if (file.writeError || !file.sync()) {
    error("write header failed");
  }
}

void loop(void) {
  
  // clear print error
  file.writeError = 0;
  delay((LOG_INTERVAL -1) - (millis() % LOG_INTERVAL));
  
  if (Uart.available()){
    if (ledson) {
      ledblevel += 50;
      analogWrite (ledb,ledblevel);
    }
    //digitalWrite (ledb,HIGH);
    inByte = Uart.read();    
    file.print(inByte);
    Serial.print(inByte);
    //Serial.print(" ");
    //Serial.print(inByte,HEX);
    //Serial.print(" ");
    } else {
      //digitalWrite (ledb, LOW);
    }
    
  if (file.writeError) error("write data failed");
  
  //don't sync too often - requires 2048 bytes of I/O to SD card
  if ((millis() - syncTime) <  SYNC_INTERVAL) return;
  syncTime = millis();
  if (!file.sync()) {
    digitalWrite(ledb,LOW);
    digitalWrite(ledg,LOW);
    error("sync failed");
  } else {
    if (ledson) {
      digitalWrite(ledb,LOW);
      digitalWrite(ledg,LOW);
      for(int i = 255; i>0; i--) {
        analogWrite(ledg,i);
        delay(1);
      }
      digitalWrite(ledg,LOW);
    }
  }
  digitalWrite(ledb,LOW);
}

void requestEvent()
{
  Wire.send("hello "); // respond with message of 6 bytes
                       // as expected by master
}
