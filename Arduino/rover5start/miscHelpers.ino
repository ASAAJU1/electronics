/*$T indentinput.cpp GC 1.140 11/26/12 16:12:03 */


/*$6
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */


/*
 =======================================================================================================================
 =======================================================================================================================
 */
void serialCountdown(int count)
{
	for(int thisd = count; thisd > 0; thisd--)
	{
		Serial.println(thisd);
		delay(100);
		digitalWrite(led, HIGH);
		delay(100);
		digitalWrite(led, LOW);
		smillis = millis();
		while(millis() - smillis < 800)
		{
			if(Serial.available() > 0)
			{
				return;
			}
		}

		/*
		 * delay(800);
		 */
	}
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void writeSettingsee()
{
	/*~~~~~~~~~*/
	int addr = 0;
	/*~~~~~~~~~*/

	EEPROM.write(addr, 17); /* Use 17 as magic key */
	addr += 2;	/* Skip address 1, addr 1 used to store count */
	EEPROM.write(addr, numChannels);	/* store num channels to verify on read */
	for(int i = 0; i < numChannels; i++)
	{
		addr += 1;
		EEPROM.write(addr, speedPins[i]);
#ifdef DEBUG
		Serial.print(F("Writing speedPins["));
		Serial.print(i);
		Serial.print(F("] \tEEPROM address: "));
		Serial.println(addr);
#endif
	}

	for(int i = 0; i < numChannels; i++)
	{
		addr += 1;
		EEPROM.write(addr, dirPins[i]);
#ifdef DEBUG
		Serial.print(F("Writing dirPins["));
		Serial.print(i);
		Serial.print(F("] \tEEPROM address: "));
		Serial.println(addr);
#endif
	}

	for(int i = 0; i < numChannels; i++)
	{
		addr += 1;
		EEPROM.write(addr, interruptchannels[i]);
#ifdef DEBUG
		Serial.print(F("Writing interruptchannels["));
		Serial.print(i);
		Serial.print(F("] \tEEPROM address: "));
		Serial.println(addr);
#endif
	}

	for(int i = 0; i < numChannels; i++)
	{
		addr += 1;
		EEPROM.write(addr, currentPins[i]);
#ifdef DEBUG
		Serial.print(F("Writing currentPins["));
		Serial.print(i);
		Serial.print(F("] \tEEPROM address: "));
		Serial.println(addr);
#endif
	}

	addr += 1;
	EEPROM.write(addr, 250);
	addr += 1;
	EEPROM.write(1, addr);

	/*~~~~~~*/
	/* Store the count of blocks in block #1 */
	byte	x;
	/*~~~~~~*/

	x = createChecksum(0, addr);
	EEPROM.write(addr, x);
#ifdef DEBUG
	Serial.print(F("Checksum "));
	Serial.print(x);
	Serial.print(F(" written to address: "));
	Serial.print(addr);
	Serial.print(F(" at "));
	Serial.print(millis());
	Serial.println(F(" millis"));
#endif
	Serial.println(F("verify checksum: "));
	if(verifyChecksum(0, addr + 1) != 0)
	{
		Serial.println(F("Invalid Checksum!"));
	}
	else
	{
		Serial.println(F("Checksum good"));
	}
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
int verifyChecksum(int startAddress, int count)
{
	/*~~~~~~~~~~*/
	byte	c;
	byte	x = 0;
	/*~~~~~~~~~~*/

	for(int i = startAddress; i < startAddress + count; i++)
	{
		c = EEPROM.read(i);
		x += c;
#ifdef DEBUG
		Serial.print(F("Address:\t"));
		Serial.print(i);
		Serial.print(F("\tValue:\t"));
		Serial.print(c);
		Serial.print(F("\tRunningX:\t"));
		Serial.print(x);
		Serial.print(F("\tmillis:\t"));
		Serial.println(millis());
#endif
	}

	return x;
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
int createChecksum(int startAddress, int count)
{

	/*~~~~~~~~~~*/
	/* TODO: Check for magic key. */
	byte	c;
	byte	x = 0;
	/*~~~~~~~~~~*/

	for(int i = startAddress; i < startAddress + count; i++)
	{
		c = EEPROM.read(i);
		x += c;
#ifdef DEBUG
		Serial.print(F("Address:\t"));
		Serial.print(i);
		Serial.print(F("\tValue:\t"));
		Serial.print(c);
		Serial.print(F("\tRunningX:\t"));
		Serial.print(x);
		Serial.print(F("\tmillis:\t"));
		Serial.println(millis());
#endif
	}

	return 256 - x;
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
byte readSettingsee(int startAddress)
{

	/* TODO: Make this do something */
	return 0;
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void processCMD()
{
	while(processSerialCMD() != 0)
	{ }
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
int processSerialCMD()
{

	/* TODO: Add the command processing structure */
	if(Serial.available() > 0)
	{
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		byte	choice = Serial.read();
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

		switch(choice)
		{
		case '1':	Serial.println("1"); break;
		case 'S':	runSerialMenu(); return 0;
		default:	return 1;
		}
	}

	return 0;
}
