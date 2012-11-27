/*$T indentinput.cpp GC 1.140 11/26/12 16:11:52 */


/*$6
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */


/*
 =======================================================================================================================
 =======================================================================================================================
 */
void runSerialMenu()
{
	while(serialMenuStart() != 0)
	{ }
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
int serialMenuStart()
{
	/*~~~~~~~~~~~~~~~~~~~*/
	unsigned int	driveC;
	/*~~~~~~~~~~~~~~~~~~~*/

	Serial.println();
	Serial.println(F("============================================================"));
	Serial.print(F("rover5start compiled at: "));
	Serial.print(__TIME__);
	Serial.print(F(" on "));
	Serial.print(__DATE__);
	Serial.println(".");
	Serial.print(F("Compiled with Arduino version: "));
	Serial.println(ARDUINO);
	Serial.println(F("============================================================"));
	Serial.println("1. Print Operating commands");
	Serial.println("2. Print Pin Configurations");
	Serial.println("3. Enable/Disable Tank mode");
	Serial.println("L. Left  300");
	Serial.println("R. Right 300");
	Serial.println("W. Write Settings to EEPROM");
	Serial.println("C. Reset Current Overload");
	Serial.println(F("P. Process Serial Command mode"));
	Serial.println(F("E. Read Settings from EEPROM"));
	Serial.println("");
	Serial.println("X. Exit");
	Serial.println(F("============================================================"));
	Serial.print("Enter your choice: ");
	while(Serial.available() < 1)
	{
		delay(50);
		digitalWrite(led, HIGH);
		delay(50);
		digitalWrite(led, LOW);
	}

	if(Serial.available() > 0)
	{
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		char	choice = Serial.read();
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

		Serial.println(choice);
		delay(10);
		switch(choice)
		{
		case '1':
			Serial.println("Operatings commands");
			break;

		case '2':
			setupMenuPinouts();
			break;

		case '3':
			Serial.println("Tank mode");
			break;

		case 'L':
			directLeft();
			driveC = driveClicks(300, 200);
			Serial.print(F("Drive Clicks Final Destination: "));
			Serial.println(driveC);
			break;

		case 'R':
			directRight();
			driveC = driveClicks(300, 200);
			Serial.print(F("Drive Clicks Final Destination: "));
			Serial.println(driveC);
			break;

		case 'W':
			writeSettingsee();
			break;

		case 'C':
			currentO = false;
			break;

		case 'P':
			processCMD();
			break;

		case 'E':
			readSettingsee(0);
			break;

		case 'X':
			Serial.println("Exiting...");
			return 0;

		default:
			Serial.println("Unknown command");
			return 1;
		}

		return 2;
	}
	else
	{
		return 3;
	}
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
int setupMenuPinouts()
{
	Serial.println();
	Serial.println(F("============================================================"));
	Serial.println(F("== Printing Pinouts  ======================================="));
	Serial.println(" CH1 Front Left       Front Right CH2");
	Serial.print("  Direction: ");
	Serial.print(dirPins[0]);
	Serial.print("        Direction: ");
	Serial.println(dirPins[1]);
	Serial.print("  Speed: ");
	Serial.print(speedPins[0]);
	Serial.print("             Speed: ");
	Serial.println(speedPins[1]);
	Serial.print("  Interrupt: ");
	Serial.print(interruptchannels[0]);
	Serial.print("         Interrupt: ");
	Serial.println(interruptchannels[1]);
	Serial.print("  MCurrent: A");
	Serial.print(currentPins[0]);
	Serial.print("         MCurrent: A");
	Serial.println(currentPins[1]);
	Serial.println();
	Serial.println(" CH3 Rear  Left       Rear  Right CH4");
	Serial.print("  Direction: ");
	Serial.print(dirPins[2]);
	Serial.print("        Direction: ");
	Serial.println(dirPins[3]);
	Serial.print("  Speed: ");
	Serial.print(speedPins[2]);
	Serial.print("              Speed: ");
	Serial.println(speedPins[3]);
	Serial.print("  Interrupt: ");
	Serial.print(interruptchannels[2]);
	Serial.print("        Interrupt: ");
	Serial.println(interruptchannels[3]);
	Serial.print("  MCurrent: A");
	Serial.print(currentPins[2]);
	Serial.print("         MCurrent: A");
	Serial.println(currentPins[3]);
	Serial.println(F("============================================================"));

	return 0;
}
