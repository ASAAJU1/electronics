/*$T indentinput.cpp GC 1.140 11/26/12 16:11:18 */

/*
 * rover5start This is an arduino program meant to be easily modified by someone
 * relatively new to arduino. This is developed on an arduino mega, but should be
 * easily changed for other platforms. Be sure to configure the following:
 * numChannels Set to the number of channels you have R5tank Do you have tank
 * treads? The program assumes that left channels are odd, and right are even.
 * Currently CH1 = front left, CH2 = front right, CH3 = rear left, CH4 = rear
 * right
 */


/*$6
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 */


#include <EEPROM.h>
#include <MemoryFree.h>

/* Rover 5 basic control */
unsigned int			gospeed = 250;
#define DEBUG	1
const byte				numChannels = 4;
boolean					R5tank = true;
boolean					currentO = false;	/* flag to indicate current overload happened */
int						currentMax = 200;	/* Max raw ADC value, before setting currentOverload */

/* These are the pin assignment for PWM */
const byte				speedPins[] = { 6, 7, 8, 9 };

/* Pins for direction */
const byte				dirPins[] = { 22, 23, 24, 25 };

/* Interrupt pin assignments */
const byte				interruptchannels[] = { 2, 3, 18, 19 };

/* Current sense Analog Pin assignments */
const byte				currentPins[] = { 0, 1, 2, 3 }; /* Use analog pin numbers */

/* Misc used to count millis */
unsigned long			smillis = 0;
unsigned long			tmillis = 0;
unsigned long			elapsed;

/* counters for the wheel encoders */
volatile unsigned int	intL = 0;
volatile unsigned int	intR = 0;
volatile unsigned int	encFL = 0;	/* front left */
volatile unsigned int	encFR = 0;	/* front right */
volatile unsigned int	encRL = 0;	/* rear left */
volatile unsigned int	encRR = 0;	/* rear right */

/* used to store motor current */
int						current1, current2, current3, current4;
int						current[numChannels];

/* store the highest current per motor */
int						currentH[numChannels];

/* store when highest reading happened */
unsigned long			currentHm[numChannels];
const int				numReadingsc = 10;
int						currentReading[numChannels][numReadingsc];

const int				led = 13;

/*
 =======================================================================================================================
 =======================================================================================================================
 */

void setup()
{

	/* setup output pins right away */
	for(int i = 0; i < numChannels; i++)
	{
		pinMode(speedPins[i], OUTPUT);
		digitalWrite(speedPins[i], LOW);
		pinMode(dirPins[i], OUTPUT);
	}

	/* start serial. print program info */
	Serial.begin(115200);
	Serial.print("rover5start compiled at: ");
	Serial.print(__TIME__);
	Serial.print(" on ");
	Serial.print(__DATE__);
	Serial.println(".");
//Serial.print(F("Free Memory: "));
//Serial.println(freeMemory());
	Serial.print("Press s to enter setup:");
	Serial.flush();
	attachInterrupt(0, intFL, LOW);
	attachInterrupt(1, intFR, LOW);

	pinMode(led, OUTPUT);
	digitalWrite(led, LOW);
	smillis = millis();
	while(millis() - smillis < 2000ul)
	{
		if(Serial.available() > 0)
		{
			break;
		}
	}

	/*
	 * delay(2000);
	 */
	if(Serial.available() > 0)
	{
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		char	choice = Serial.read();
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

		if(choice == 's')
		{
			runSerialMenu();
		}
	}
	else
	{
		Serial.println(" End of Setup");
	}
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void loop()
{
	testRover();
	if(Serial.available() > 0)
	{
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
		char	choice = Serial.read();
		/*~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

		if(choice == 's')
		{
			runSerialMenu();
		}
	}
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void directF()
{
	digitalWrite(dirPins[0], HIGH);
	digitalWrite(dirPins[1], HIGH);
	digitalWrite(dirPins[2], LOW);
	digitalWrite(dirPins[3], LOW);
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void directR()
{
	digitalWrite(dirPins[0], LOW);
	digitalWrite(dirPins[1], LOW);
	digitalWrite(dirPins[2], HIGH);
	digitalWrite(dirPins[3], HIGH);
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void directLeft()
{
	digitalWrite(dirPins[0], LOW);
	digitalWrite(dirPins[1], HIGH);
	digitalWrite(dirPins[2], HIGH);
	digitalWrite(dirPins[3], LOW);
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void directRight()
{
	digitalWrite(dirPins[0], HIGH);
	digitalWrite(dirPins[1], LOW);
	digitalWrite(dirPins[2], LOW);
	digitalWrite(dirPins[3], HIGH);
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void directSTOP()
{

	/*
	 * E4=2, E5=3, E3=5 ;
	 * H3=6, H4=7, H5=9, H6=8 ;
	 * G5=4 ;
	 * B4=10, B5=11, B6=12, B7=13 ;
	 * PORTH &= B10000111;
	 */
	for(int i = 0; i < numChannels; i++)
	{
		digitalWrite(speedPins[i], LOW);
	}

	digitalWrite(led, LOW);
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void intFL()
{
	intL++;
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void intFR()
{
	intR++;
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
void reportStuff()
{
	Serial.print(intL);
	Serial.print(",");
	Serial.print(intR);

	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
	unsigned int	t = gatherCurrentReadings();
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

	Serial.print(":");
	Serial.print(current1);
	Serial.print(",");
	Serial.print(current2);
	Serial.print(",");
	Serial.print(current3);
	Serial.print(",");
	Serial.print(current4);
	Serial.print(":");
	Serial.print(t);
	Serial.print(":");
	Serial.println(millis());
}

/*
 =======================================================================================================================
 =======================================================================================================================
 */
unsigned int gatherCurrentReadings()
{
	smillis = millis();
	for(int i = 0; i < numReadingsc; i++)
	{
		for(int j = 0; j < numChannels; j++)
		{
			currentReading[j][i] = analogRead(currentPins[i]);
			if(currentReading[j][i] > currentH[j])
			{
				currentH[j] = currentReading[j][i];
				currentHm[j] = millis();
			}

			if(currentReading[j][i] > currentMax)
			{
				currentO = true;
				return 0;
			}
		}
	}

	/*~~~~~~~~~~~~~~~~~~~*/
	unsigned int	t1 = 0;
	unsigned int	t2 = 0;
	unsigned int	t3 = 0;
	unsigned int	t4 = 0;
	/*~~~~~~~~~~~~~~~~~~~*/

	for(int i = 0; i < numReadingsc; i++)
	{
		t1 += currentReading[0][i];
		t2 += currentReading[1][i];
		t3 += currentReading[2][i];
		t4 += currentReading[3][i];
	}

	current1 = t1 / numReadingsc;
	current2 = t2 / numReadingsc;
	current3 = t3 / numReadingsc;
	current4 = t4 / numReadingsc;

	tmillis = millis();

	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
	unsigned int	e = tmillis - smillis;
	/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/

	return e;
}
