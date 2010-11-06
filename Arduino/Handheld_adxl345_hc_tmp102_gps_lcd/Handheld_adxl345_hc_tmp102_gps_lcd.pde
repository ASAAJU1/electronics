// ADXL345 -- CS HIGH SDO LOW
/////////////////////////////////////////////////////////////////////////////////////////
// I2C Scanning function from todbot
// http://todbot.com/blog/2009/11/29/i2cscanner-pde-arduino-as-i2c-bus-scanner/
// http://todbot.com/arduino/sketches/I2CScanner/I2CScanner.pde
/////////////////////////////////////////////////////////////////////////////////////////
// Sd functions based off of SdFat Analog logger
// also sdfatinfo
/////////////////////////////////////////////////////////////////////////////////////////
// ADXL345 code from forum??
/////////////////////////////////////////////////////////////////////////////////////////
// HMC6352 code from forum???
/////////////////////////////////////////////////////////////////////////////////////////
// Other code credits?
/////////////////////////////////////////////////////////////////////////////////////////
#include "config.h"
#define ADXL345 (0x53)    //ADXL345 device address
#define TO_READ (6)        //num of bytes we are going to read each time (two bytes for each axis)

byte buff[TO_READ] ;    //6 bytes buffer for saving data read from the device
char str[512];          //string buffer to transform data before sending it to the serial port
byte start_address = 1;
byte end_address = 100;

////////////////////////////////////////
int compassAddress = 0x42 >> 1;  // From datasheet compass address is 0x42
// shift the address 1 bit right, the Wire library only needs the 7
// most significant bits for the address
int reading = 0; 
////////////////////////////////////////
//int clockAddress = 0x68;  // This is the I2C address
//int command = 0;  // This is the command char, in ascii form, sent from the serial port     
long previousMillis = 0;  // will store last time Temp was updated
//byte second, minute, hour, dayOfWeek, dayOfMonth, month, year;
//byte test; 
////////////////////////////////////////
//int RECV_PIN = 7;
//IRrecv irrecv(RECV_PIN);
//decode_results results;

// A simple data logger for the Arduino analog pins
#define ECHO_TO_SERIAL   1 // echo data to serial port
#define WAIT_TO_START    1 // Wait for serial input in setup()
#define DEBUG            0 // Turn on or off Debug statements
int LOG_INTERVAL = 500; // mills between entries
int SYNC_INTERVAL = 1000; // mills between calls to sync()
uint32_t syncTime = 0;     // time of last sync()
////////////////////////////////////////
int lcdBLP = 9;  // LCD Backlight Pin
int lcdBL = 64;  // LCD Backlight PWM Brightness
////////////////////////////////////////

#include <SdFat.h>
#include <SdFatUtil.h>
#include <Wire.h>
#include "RTClib.h"
//#include <IRremote.h>
//#include <NewSoftSerial.h>
//NewSoftSerial nss2(4, 5);
// include the library code:
#include <LiquidCrystal.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 7, 6, 5, 4, 3);

extern "C" { 
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}
////////////////////////////////////////
// offset to partition table
#define PART_OFFSET (512-64-2) 
//global for card erase sector size
uint32_t sectorSize; 

Sd2Card card;
SdVolume volume;
SdFile root;
SdFile file;
////////////////////////////////////////
RTC_DS1307 RTC; // define the Real Time Clock object
////////////////////////////////////////

// store error strings in flash to save RAM
#define error(s) error_P(PSTR(s))

void error_P(const char* str) {
	lcd.clear();
	lcd.print("error: ");
	PgmPrint("error: ");
	SerialPrintln_P(str);
	lcd.print(str);
	if (card.errorCode()) {
		PgmPrint("uSD error: ");
		lcd.setCursor(0,1);
		lcd.print("uSD error: ");
		Serial.print(card.errorCode(), HEX);
		Serial.print(',');
		Serial.println(card.errorData(), HEX);
		lcd.print(card.errorCode(), HEX);
		lcd.print(',');
		lcd.print(card.errorData(), HEX);
	}  // end if
	while(1);
}  // end of error_P

void setup(void) {
	Serial.begin(9600);
	analogWrite(lcdBLP, lcdBL);  
	lcd.begin(16,2);
	lcd.print("HHS alpha 0.0.4");
	lcd.setCursor(0, 1);
	lcd.print(__TIME__);
	lcd.print(" ");
	lcd.print(__DATE__);
	Serial.println();
	Serial.print("Handheld Sensors Logger. Alpha 0.0.4  ");
	Serial.print("Compiled on ");
	Serial.print(__DATE__);
	Serial.print(" at ");
	Serial.print( __TIME__);
	Serial.println();

#if WAIT_TO_START
	Serial.println("Type any character to start, or press i for info");
	while (!Serial.available());
	int inByte = Serial.read();
	//Serial.println(inByte);
	if (inByte == 'i') {
		menuSetup(1);
	}
#endif //WAIT_TO_START

	// initialize the SD card at SPI_HALF_SPEED to avoid bus errors with
	// breadboards.  use SPI_FULL_SPEED for better performance.
	if (!card.init(SPI_HALF_SPEED)) error("card.init failed");

	// initialize a FAT volume
	if (!volume.init(&card)) error("volume.init failed");

	// open root directory
	if (!root.openRoot(&volume)) error("openRoot failed");

	// create a new file
	char name[] = "HHSLOG00.CSV";
	for (uint8_t i = 0; i < 100; i++) {
		name[6] = i/10 + '0';
		name[7] = i%10 + '0';
		if (file.open(&root, name, O_CREAT | O_EXCL | O_WRITE)) break;
	}
	if (!file.isOpen()) error ("file.create");
#if ECHO_TO_SERIAL 
	Serial.print("Logging to: ");
	Serial.println(name);
#endif //ECHO_TO_SERIAL

	// write header
	file.writeError = 0;
	file.print("unixTime, Compass, X,Y,Z, YYYY/MM/DD HH:MM:SS,millis");
#if ECHO_TO_SERIAL 
	Serial.print("unixTime, Compass, X,Y,Z, YYYY/MM/DD HH:MM:SS,millis");
#endif //ECHO_TO_SERIAL
	file.println();  
#if ECHO_TO_SERIAL
	Serial.println();
#endif  //ECHO_TO_SERIAL

	if (file.writeError || !file.sync()) {
		error("write header failed");
	}

	Wire.begin();        // join i2c bus (address optional for master)
	//Turning on the ADXL345
	writeTo(ADXL345, 0x2D, 0);      
	writeTo(ADXL345, 0x2D, 16);
	writeTo(ADXL345, 0x2D, 8);
#if ECHO_TO_SERIAL
	Serial.println("End of setup");
#endif  //ECHO_TO_SERIAL

}

void loop(void) {
	// clear print error
	file.writeError = 0;
	delay((LOG_INTERVAL -1) - (millis() % LOG_INTERVAL));
	////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////
	DateTime now = RTC.now();
	file.print(now.unixtime());
	file.print(", ");  
#if ECHO_TO_SERIAL
	Serial.print(now.unixtime());
	Serial.print(", ");
#endif //ECHO_TO_SERIAL    
	////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////
	reading = readCompass();
	file.print(reading);
	file.print(", ");  
#if ECHO_TO_SERIAL
	Serial.print(reading);
	Serial.print(", ");
#endif //ECHO_TO_SERIAL
	////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////
	int regAddress = 0x32;    //first axis-acceleration-data register on the ADXL345
	int x, y, z;

	readFrom(ADXL345, regAddress, TO_READ, buff); //read the acceleration data from the ADXL345

	//each axis reading comes in 10 bit resolution, ie 2 bytes.  Least Significat Byte first!!
	//thus we are converting both bytes in to one int
	x = (((int)buff[1]) << 8) | buff[0];  
	y = (((int)buff[3])<< 8) | buff[2];
	z = (((int)buff[5]) << 8) | buff[4];

	//we send the x y z values as a string to the serial port
	//sprintf(str, "%d,%d,%d,", x, y, z);  
	//Serial.print(str);
	file.print(x);
	file.print(",");
	file.print(y);
	file.print(",");
	file.print(z);
	file.print(",");
#if ECHO_TO_SERIAL
	Serial.print(x);
	Serial.print(",");
	Serial.print(y);
	Serial.print(",");
	Serial.print(z);
	Serial.print(",");
#endif //ECHO_TO_SERIAL
	////////////////////////////////////////////////////////////
	////////////////////////////////////////////////////////////
	file.print(" ");
	file.print(now.year(), DEC);
	file.print('/');
	file.print(now.month(), DEC);
	file.print('/');
	file.print(now.day(), DEC);
	file.print(' ');
	file.print(now.hour(), DEC);
	file.print(':');
	file.print(now.minute(), DEC);
	file.print(':');
	file.print(now.second(), DEC);
	file.print(",");
#if ECHO_TO_SERIAL
	Serial.print(" ");
	Serial.print(now.year(), DEC);
	Serial.print('/');
	Serial.print(now.month(), DEC);
	Serial.print('/');
	Serial.print(now.day(), DEC);
	Serial.print(' ');
	Serial.print(now.hour(), DEC);
	Serial.print(':');
	Serial.print(now.minute(), DEC);
	Serial.print(':');
	Serial.print(now.second(), DEC);
	Serial.print(",");
#endif //ECHO_TO_SERIAL
	//printDT();
	////////////////////////////////////////////////////////////
	//////////////////////////////////////////////////////////// 
	// log time
	uint32_t m = millis();
	file.print(m);  
#if ECHO_TO_SERIAL
	Serial.print(m);
#endif //ECHO_TO_SERIAL      
	//End of loop run. Send out newline.
	file.println();  
#if ECHO_TO_SERIAL
	Serial.println();
#endif //ECHO_TO_SERIAL
	////////////////////////////////////////////
	// print to lcd 
	////////////////////////////////////////////
	lcd.clear();
	lcd.print(reading);
	lcd.setCursor(5,0);
	lcd.print(m);
	lcd.setCursor(0,1);
	lcd.print(x);
	lcd.print(",");
	lcd.print(y);
	lcd.print(",");
	lcd.print(z);


	if (file.writeError) error("write data failed");

	//don't sync too often - requires 2048 bytes of I/O to SD card
	if ((millis() - syncTime) <  SYNC_INTERVAL) return;
	syncTime = millis();
	if (!file.sync()) error("sync failed");
}  // end of loop



//---------------- Functions
//Writes val to address register on device
void writeTo(int device, byte address, byte val) {
	Wire.beginTransmission(device); //start transmission to device
	Wire.send(address);        // send register address
	Wire.send(val);        // send value to write
	Wire.endTransmission(); //end transmission
}

//reads num bytes starting from address register on device in to buff array
void readFrom(int device, byte address, int num, byte buff[]) {
	Wire.beginTransmission(device); //start transmission to device
	Wire.send(address);        //sends address to read from
	Wire.endTransmission(); //end transmission

	Wire.beginTransmission(device); //start transmission to device
	Wire.requestFrom(device, num);    // request 6 bytes from device

	int i = 0;
	while(Wire.available())    //device may send less than requested (abnormal)
	{
		buff[i] = Wire.receive(); // receive a byte
		i++;
	}
	Wire.endTransmission(); //end transmission
}

int readCompass(void) {
	////////////////////////////////////////////////
	// step 1: instruct sensor to read echoes 
	Wire.beginTransmission(compassAddress);  // transmit to device
	// the address specified in the datasheet is 66 (0x42) 
	// but i2c adressing uses the high 7 bits so it's 33 
	Wire.send('A');          // command sensor to measure angle  
	Wire.endTransmission();  // stop transmitting 

	// step 2: wait for readings to happen 
	delay(10);               // datasheet suggests at least 6000 microseconds 

	// step 3: request reading from sensor 
	Wire.requestFrom(compassAddress, 2);  // request 2 bytes from slave device #33 

	// step 4: receive reading from sensor 
	if(2 <= Wire.available())     // if two bytes were received 
	{ 
		reading = Wire.receive();   // receive high byte (overwrites previous reading) 
		reading = reading << 8;     // shift high byte to be high 8 bits 
		reading += Wire.receive();  // receive low byte as lower 8 bits 
		reading /= 10;
		//Serial.print(reading);    // print the reading 
		//Serial.print(",");
	} 
	return reading;
} 

//void printDT(void) {
//}


uint8_t cidDmp(void) {
	cid_t cid;
	if (!card.readCID(&cid)) {
		PgmPrint("readCID failed");
		sdError();
		return false;
	}
	PgmPrint("\nManufacturer ID: ");
	Serial.println(cid.mid, HEX);
	PgmPrint("OEM ID: ");
	Serial.print(cid.oid[0]);
	Serial.println(cid.oid[1]);
	PgmPrint("Product: ");
	for (uint8_t i = 0; i < 5; i++) {
		Serial.print(cid.pnm[i]);
	}
	PgmPrint("\nVersion: ");
	Serial.print(cid.prv_n, DEC);
	Serial.print('.');
	Serial.println(cid.prv_m, DEC);
	PgmPrint("Serial number: ");
	Serial.println(cid.psn);
	PgmPrint("Manufacturing date: ");
	Serial.print(cid.mdt_month);
	Serial.print('/');
	Serial.println(2000 + cid.mdt_year_low + (cid.mdt_year_high <<4));
	Serial.println();
	return true;
}

uint8_t csdDmp(void) {
	csd_t csd;
	uint8_t eraseSingleBlock;
	uint32_t cardSize = card.cardSize();
	if (cardSize == 0 || !card.readCSD(&csd)) {
		PgmPrintln("readCSD failed");
		sdError();
		return false;
	}
	if (csd.v1.csd_ver == 0) {
		eraseSingleBlock = csd.v1.erase_blk_en;
		sectorSize = (csd.v1.sector_size_high << 1) | csd.v1.sector_size_low;
	}
	else if (csd.v2.csd_ver == 1) {
		eraseSingleBlock = csd.v2.erase_blk_en;
		sectorSize = (csd.v2.sector_size_high << 1) | csd.v2.sector_size_low; 
	}
	else {
		PgmPrintln("csd version error");
		return false;
	}
	sectorSize++;
	PgmPrint("cardSize: ");
	Serial.print(cardSize);
	PgmPrintln(" (512 byte blocks)");
	PgmPrint("flashEraseSize: ");
	Serial.print(sectorSize, DEC);
	PgmPrintln(" blocks");
	PgmPrint("eraseSingleBlock: ");
	if (eraseSingleBlock) {
		PgmPrintln("true");
	}
	else {
		PgmPrintln("false");
	}
	return true;
}
// print partition table
uint8_t partDmp(void) {
	part_t pt;
	PgmPrintln("\npart,boot,type,start,length");  
	for (uint8_t ip = 1; ip < 5; ip++) {
		if (!card.readData(0, PART_OFFSET + 16*(ip-1), 16, (uint8_t *)&pt)) {
			PgmPrint("read partition table failed");
			sdError();
			return false;
		}
		Serial.print(ip, DEC);
		Serial.print(',');
		Serial.print(pt.boot,HEX);
		Serial.print(',');
		Serial.print(pt.type, HEX);
		Serial.print(',');
		Serial.print(pt.firstSector);
		Serial.print(',');
		Serial.println(pt.totalSectors); 
	}
	return true;
}

void volDmp(void) {
	PgmPrint("\nVolume is FAT");
	Serial.println(volume.fatType(), DEC);
	PgmPrint("blocksPerCluster: ");
	Serial.println(volume.blocksPerCluster(), DEC);
	PgmPrint("clusterCount: ");
	Serial.println(volume.clusterCount());
	PgmPrint("fatStartBlock: ");
	Serial.println(volume.fatStartBlock());
	PgmPrint("fatCount: ");
	Serial.println(volume.fatCount(), DEC);
	PgmPrint("blocksPerFat: ");
	Serial.println(volume.blocksPerFat());
	PgmPrint("rootDirStart: ");
	Serial.println(volume.rootDirStart());
	PgmPrint("dataStartBlock: ");
	Serial.println(volume.dataStartBlock());
	if (volume.dataStartBlock()%sectorSize) {
		PgmPrintln("Data area is not aligned on flash erase boundaries!");
	}
}

void sdError(void) {
	PgmPrintln("SD error");
	PgmPrint("errorCode: ");
	Serial.println(card.errorCode(), HEX);
	PgmPrint("errorData: ");
	Serial.println(card.errorData(), HEX);  
	return;
}

void printSDInfo(void) {
	uint32_t t = millis();
	// initialize the SD card at SPI_HALF_SPEED to avoid bus errors with
	// breadboards.  use SPI_FULL_SPEED for better performance.
	uint8_t r = card.init(SPI_HALF_SPEED);
	t = millis() - t;
	if (!r) {
		PgmPrintln("\ncard.init failed");
		sdError();
		return;
	}
	PgmPrint("\ninit time: ");
	Serial.println(t);
	PgmPrint("\nCard type: ");
	switch(card.type()) {
	case SD_CARD_TYPE_SD1:
		PgmPrintln("SD1");
		break;
	case SD_CARD_TYPE_SD2:
		PgmPrintln("SD2");
		break;
	case SD_CARD_TYPE_SDHC:
		PgmPrintln("SDHC");
		break;
	default:
		PgmPrintln("Unknown");
	}
	if(!cidDmp()) return;
	if(!csdDmp()) return;
	if(!partDmp()) return;
	if (!volume.init(&card)) {
		PgmPrintln("\nvol.init failed");
		sdError();
		return;
	}
	volDmp();
}

// Scan the I2C bus between addresses from_addr and to_addr.
// On each address, call the callback function with the address and result.
// If result==0, address was found, otherwise, address wasn't found
// (can use result to potentially get other status on the I2C bus, see twi.c)
// Assumes Wire.begin() has already been called
void scanI2CBus(byte from_addr, byte to_addr, void(*callback)(byte address, byte result)) {
	byte rc;
	byte data = 0; // not used, just an address to feed to twi_writeTo()
	for( byte addr = from_addr; addr <= to_addr; addr++ ) {
		rc = twi_writeTo(addr, &data, 0, 1);
		callback( addr, rc );
	}
}

// Called when address is found in scanI2CBus()
// Feel free to change this as needed
// (like adding I2C comm code to figure out what kind of I2C device is there)
void scanFunc( byte addr, byte result ) {
	Serial.print("addr: ");
	Serial.print(addr,DEC);
	Serial.print( (result==0) ? " found!":"       ");
	Serial.print( (addr%4) ? "\t":"\n");
}

int menuSetup(int opt1) {
	int ii = 1;
	char x_buffer[3];
	char y_buffer[4];
	int j = 0;
	while (ii == 1) {
		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrint("=====");
		Serial.print(" information ");
		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrintln("=====");
		lcd.clear();
		lcd.print("Sample: ");
		lcd.print(1000.0/LOG_INTERVAL);
		lcd.print("Hz");
		lcd.setCursor(0,1);
		lcd.print("Sync: ");
		lcd.print(1000.0/SYNC_INTERVAL);
		lcd.print("Hz");
		Serial.print("Sample Rate: ");
		Serial.print(1000.0/LOG_INTERVAL);
		Serial.print("Hz  Sync Rate: ");
		Serial.print(1000.0/SYNC_INTERVAL);
		Serial.println("Hz");
		Serial.println("ADXL345:\tActive\t HMC6352:\tActive");
		Serial.println("RTC:    \tActive\t TMP102: \tActive");

		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrint("=====");
		Serial.print(" Setup  Menu ");
		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrint("=====");
		PgmPrintln("=====");

		Serial.println("1. Scan I2C Bus");
		Serial.println("2. SD Info");
		Serial.println("3. Change Sample Rate");
		Serial.println("4. Change Sync Rate");
		Serial.println("5. Change LCD Brightness");
		Serial.println("0. Exit");
		while (!Serial.available());
		if (Serial.available() > 0) {
			char choice = Serial.read();
			Serial.flush();
			//Serial.println(choice);
			delay(10);
			switch (choice) {
			case '1':
				Serial.println("Scan I2C Bus");
				Serial.print("starting scanning of I2C bus from ");
				Serial.print(start_address,DEC);
				Serial.print(" to ");
				Serial.print(end_address,DEC);
				Serial.println("...");

				// start the scan, will call "scanFunc()" on result from each address
				scanI2CBus( start_address, end_address, scanFunc );

				Serial.println("\ndone");
				break;
			case '2':
				Serial.println("uSD Card info");
				printSDInfo();
				break;
			case '3':
				Serial.println("Enter new sample rate in milliseconds(xxx): ");
				while (Serial.available()<3);
				//char x_buffer[3];
				if (Serial.available()){
					for (j = 0; j < 3; j++) {
						x_buffer[j] = Serial.read();
						#if DEBUG
						Serial.print(" ");
						Serial.print(j, DEC);
						Serial.print(" ");
						Serial.print(x_buffer[j]);
						Serial.print(" ");
						#endif
					}
					LOG_INTERVAL = atoi(x_buffer);
					Serial.println(LOG_INTERVAL);
					Serial.flush();
				}
				break;
			case '4':
				Serial.println("Enter new sync rate in milliseconds(xxxx): ");
				while (Serial.available()<4);
				//char y_buffer[4];
				if (Serial.available()){
					for (j = 0; j < 4; j++) {
						y_buffer[j] = Serial.read();
						#if DEBUG
						Serial.print(" ");
						Serial.print(j, DEC);
						Serial.print(" ");
						Serial.print(y_buffer[j]);
						Serial.print(" ");
						#endif
					}
					SYNC_INTERVAL = atoi(y_buffer);
					Serial.println(SYNC_INTERVAL);
					Serial.flush();
					for (j = 0; j < 4; j++) {
						y_buffer[j] = 0;
					}
				}
				break;
			case '5':
				Serial.println("Enter new lcd backlight value 000-255: ");
				while (Serial.available()<3);
				//char x_buffer[3];
				if (Serial.available()){
					for (j = 0; j <3; j++) {
						x_buffer[j] = Serial.read();
						#if DEBUG
						Serial.print(" ");
						Serial.print(j, DEC);
						Serial.print(" ");
						Serial.print(x_buffer[j]);
						Serial.print(" ");
						#endif
					}
					lcdBL = atoi(x_buffer);
					Serial.flush();
					Serial.print("Setting LCD Backlight to ");
					Serial.print(lcdBL);
					Serial.print(". ");
					analogWrite(lcdBLP, lcdBL);
					Serial.print(lcdBL/255.0 * 100.0);
					Serial.println("%");
				}
				break;
			case '0':
				ii = 0;
				//return 0;
				break;
				
			} // End of switch
		} // end of if
	} // end of while
} // end of menusetup


