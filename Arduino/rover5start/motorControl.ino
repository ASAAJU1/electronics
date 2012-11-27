/*$T indentinput.cpp GC 1.140 11/26/12 16:12:25 */


/*$6
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */


/*
 =======================================================================================================================
 =======================================================================================================================
 */
void testRover()
{
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
	unsigned long	previousMillis = 0;
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

	serialCountdown(5);
	directF();
	digitalWrite(led, HIGH);
	for(int i = 0; i < numChannels; i++)
	{
		analogWrite(speedPins[i], gospeed);
	}

	/*
	 * delay(1500);
	 */
	while(intL <= 300)
	{
		if(Serial.available() > 0)
		{
			directSTOP();
			return;
		}

		reportStuff();
		if(currentO) break;
	}

	while(gospeed > 70)
	{
		if(Serial.available() > 0)
		{
			directSTOP();
			return;
		}

		gospeed -= 10;
		for(int i = 0; i < numChannels; i++)
		{
			analogWrite(speedPins[i], gospeed);
		}

		previousMillis = millis();
		while(millis() - previousMillis < 1000ul)
		{
			Serial.print(F("\t"));
			Serial.print(gospeed);
			Serial.print(F("\t"));
			reportStuff();
			if(currentO)
			{
				break;
			}
		}

		if(currentO)
		{
			break;
		}
	}

	directSTOP();

	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
	unsigned int	intLtmp = intL;
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

	intL = 0;
	intR = 0;

	/* Reverse */
	gospeed = 255;
	directR();
	serialCountdown(3);
	digitalWrite(led, HIGH);
	for(int i = 0; i < numChannels; i++)
	{
		analogWrite(speedPins[i], gospeed);
	}

	/*
	 * delay(1500);
	 */
	while(intL < intLtmp)
	{
		if(Serial.available() > 0)
		{
			directSTOP();
			return;
		}

		reportStuff();
		if(currentO)
		{
			break;
		}
	}

	directSTOP();
	intL = 0;
	intR = 0;
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
unsigned int driveClicks(int clicks, int gspeed)
{
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
	unsigned int	destination = intL + clicks;
	unsigned int	motorstart, motorend;
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

	if(destination < intL)
	{
		return 0;
	}

	if(gspeed > 255)
	{
		gspeed = 255;
	}

	if(gspeed < 50)
	{
		return 0;
	}

	serialCountdown(3);
	digitalWrite(led, HIGH);
	motorstart = millis();
	for(int i = 0; i < numChannels; i++)
	{
		analogWrite(speedPins[i], gospeed);
	}

	while(intL <= destination)
	{
		if(Serial.available() > 0)
		{
			break;
		}

		reportStuff();
		if(currentO)
		{
			break;
		}
	}

	directSTOP();
	motorend = millis();
	elapsed = motorend - motorstart;
	Serial.print(F("Elapsed millis: "));
	Serial.println(elapsed);

	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
	unsigned int	fdestination = intL - destination + clicks;
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

#ifdef DEBUG
	if(currentO)
	{
		Serial.print(F("Current Overload Detected: "));
		Serial.print(fdestination);
		Serial.print(F(" clicks out of "));
		Serial.print(clicks);
		Serial.println(F(" clicks driven."));
		Serial.print(F("Highest Reading. CH1: "));
		Serial.print(currentH[0]);
		Serial.print(F(" millis: "));
		Serial.print(currentHm[0]);
		Serial.print(F("\tCH2: "));
		Serial.print(currentH[1]);
		Serial.print(F(" millis: "));
		Serial.print(currentHm[1]);
		Serial.print(F("\tCH3: "));
		Serial.print(currentH[2]);
		Serial.print(F(" millis: "));
		Serial.print(currentHm[2]);
		Serial.print(F("\tCH4: "));
		Serial.print(currentH[3]);
		Serial.print(F(" millis: "));
		Serial.print(currentHm[3]);
		Serial.print(F("\tcurrentmillis: "));
		Serial.println(millis());
	}
#endif
	return fdestination;
}
