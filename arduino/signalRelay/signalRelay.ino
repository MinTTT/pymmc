 /*
 * Start blanking Mode: 20
 *   In blanking mode, zeroes will be written on the output pins when the trigger pin
 *   is low, when the trigger pin is high, the pattern set with command #1 will be
 *   applied to the output pins.
 *   Controller will return 20
 *
 * Stop blanking Mode: 21
 *   Stops blanking mode.  Controller returns 21

*/

// int inputPin = 12;
// int outputPin = 13;
// PORTB maps to Arduino digital pins 8 to 13 The two high bits (6 & 7) map to the crystal pins and are not usable
// PORTD maps to Arduino digital pins 0 to 7, we use port D as the output pins for controlling illumination.
# define inputPin 12
// outputPin used for triggering camera
# define outputPin 13
# define inputPinMap  B00010000
# define outputPinMap B00100000
# define closeState B00000000
# define onState B10111111
# define fluorMask B00111111
# define phaseGYMask B11000000
# define onMap B00111111
// # define outputPort PORTD
# define timeOut_ 1000
# define TRIGGER(MAP) \
  PORTB = (MAP & (phaseGYMask)) >> 6; \
  PORTD = (MAP & fluorMask ^ onMap) << 2;

const int SEQUENCELENGTH = 12; // this should be good enough for everybody;)
byte triggerPattern_[SEQUENCELENGTH] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
unsigned int triggerDelay_[SEQUENCELENGTH] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int patternLength_ = 0;
byte repeatPattern_ = 0;
volatile long triggerNr_ = 0;  // total # of triggers in this run (0-based)
volatile long sequenceNr_ = 0; // # of trigger in sequence (0-based)
int skipTriggers_ = 0;     // # of triggers to skip before starting to generate patterns
byte currentPattern_ = B11000000;
// const unsigned long timeOut_ = 1000;
bool blanking_ = true;  // initial as blanking mode
bool blankOnHigh_ = true;  // set high as the default mode
bool triggerMode_ = false;
bool inputTrigger_ = false;
long int triggerNumber = 0;
boolean triggerState_ = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // pinMode(inputPin, INPUT);
  // pinMode(outputPin, OUTPUT);

  DDRD = B11111100;
  DDRB = B00000011; //set pin 12 as input

  PORTB = (closeState & phaseGYMask) >> 6;
  PORTD = (closeState & fluorMask ^ onMap) << 2;  // close all pins of port D
  TRIGGER(closeState)
  
  delay(100);
}

void loop() {
  // put your main code here, to run repeatedly:
    if (Serial.available() > 0)
  {
    int inByte = Serial.read();
    switch (inByte)
    {

    // Set digital output
    case 1:
      if (waitForSerial(timeOut_))
      {
        currentPattern_ = Serial.read();
      }
      break;

    // Get digital output
    case 2:
      Serial.write(byte(2));
      Serial.write(PORTD);
      break;

    // trigger camera once
    case 3:
        // trigger camera
        inputTrigger_ = true;
        digitalWrite(outputPin, HIGH);
        delay(1);
        digitalWrite(outputPin, LOW);
        triggerNumber +=1;
        if (!blanking_)
        {
          TRIGGER(currentPattern_)
        }
      break;
    // trigger camera once, but camera will acq continously.
    case 4:
        // trigger camera
        inputTrigger_ = false;
        digitalWrite(outputPin, HIGH);
        delay(1);
        digitalWrite(outputPin, LOW);
        if (!blanking_)
        {
          TRIGGER(currentPattern_)
        }
      break;

    // Sets the specified digital pattern
    case 5:
      if (waitForSerial(timeOut_))
      {
        int patternNumber = Serial.read();
        if ((patternNumber >= 0) && (patternNumber < SEQUENCELENGTH))
        {
          if (waitForSerial(timeOut_))
          {
            triggerPattern_[patternNumber] = Serial.read();
            Serial.write(byte(5));
            Serial.write(patternNumber);
            Serial.write(triggerPattern_[patternNumber]);
            break;
          }
        }
      }
      Serial.write("n:"); //Serial.print("n:");
      break;

    

    // Sets the number of digital patterns that will be used
    case 6:
      if (waitForSerial(timeOut_))
      {
        int pL = Serial.read();
        if ((pL >= 0) && (pL <= 12))
        {
          patternLength_ = pL;
          Serial.write(byte(6));
          Serial.write(patternLength_);
        }
      }
      break;

    // Skip triggers
    case 7:
      if (waitForSerial(timeOut_))
      {
        skipTriggers_ = Serial.read();
        Serial.write(byte(7));
        Serial.write(skipTriggers_);
      }
      break;

    //  starts trigger mode
    case 8:
      if (patternLength_ > 0)
      {
        sequenceNr_ = 0;
        triggerNr_ = -skipTriggers_;
        triggerState_ = digitalRead(inputPin) == HIGH;
        TRIGGER(closeState)
        Serial.write(byte(8));
        triggerMode_ = true;
      }
      break;

    // return result from last triggermode
    case 9:
      triggerMode_ = false;
      TRIGGER(closeState)
      Serial.write(byte(9));
      Serial.write(triggerNr_);
      break;

    // Sets time interval for timed trigger mode
    // Tricky part is that we are getting an unsigned int as two bytes
    case 10:
      if (waitForSerial(timeOut_))
      {
        int patternNumber = Serial.read();
        if ((patternNumber >= 0) && (patternNumber < SEQUENCELENGTH))
        {
          if (waitForSerial(timeOut_))
          {
            unsigned int highByte = 0;
            unsigned int lowByte = 0;
            highByte = Serial.read();
            if (waitForSerial(timeOut_))
              lowByte = Serial.read();
            highByte = highByte << 8;
            triggerDelay_[patternNumber] = highByte | lowByte;
            Serial.write(byte(10));
            Serial.write(patternNumber);
            break;
          }
        }
      }
      break;

    // Sets the number of times the patterns is repeated in timed trigger mode
    case 11:
      if (waitForSerial(timeOut_))
      {
        repeatPattern_ = Serial.read();
        Serial.write(byte(11));
        Serial.write(repeatPattern_);
      }
      break;

    //  starts timed trigger mode
    case 12:
      if (patternLength_ > 0)
      {
        PORTB = closeState;
        Serial.write(byte(12));
        for (byte i = 0; i < repeatPattern_ && (Serial.available() == 0); i++)
        {
          for (int j = 0; j < patternLength_ && (Serial.available() == 0); j++)
          {
            PORTB = triggerPattern_[j];
            delay(triggerDelay_[j]);
          }
        }
        PORTB = closeState;
      }
      break;

    // Blanks output based on TTL input
    case 20:
      blanking_ = true;
      TRIGGER(closeState)
      Serial.write(byte(20));
      break;

    // Stops blanking mode
    case 21:
      blanking_ = false;
      Serial.write(byte(21));
      break;

    // Sets 'polarity' of input TTL for blanking mode
    case 22:
      if (waitForSerial(timeOut_))
      {
        int mode = Serial.read();
        if (mode == 0)
          blankOnHigh_ = true;
        else
          blankOnHigh_ = false;
      }
      Serial.write(byte(22));
      break;

    case 41:
      if (waitForSerial(timeOut_))
      {
        int pin = Serial.read();
        if (pin >= 0 && pin <= 5)
        {
          int val = analogRead(pin);
          Serial.write(byte(41));
          Serial.write(pin);
          Serial.write(highByte(val));
          Serial.write(lowByte(val));
        }
      }
      break;

    }
  }


  // stateMap(inputPin, outputPin);
if (inputTrigger_ && triggerNumber >=1){
    if (PINB & inputPinMap)
  {
    TRIGGER(currentPattern_)
  }
  else
  {
    TRIGGER(closeState)
  }
  triggerNumber -= 1;
} else if (!inputTrigger_){

  if (blanking_ && (patternLength_ == 0))
{
  if (PINB & inputPinMap)
  {
    TRIGGER(currentPattern_)

  }
  else
  {
    TRIGGER(closeState)
  }
  
}else if (blanking_ && (patternLength_ > 0))
{
  if (PINB & inputPinMap)
  {
    TRIGGER(triggerPattern_[sequenceNr_])
    // PORTD = triggerPattern_[sequenceNr_];
    sequenceNr_++;
    sequenceNr_ = sequenceNr_ % patternLength_;
  }
  else
  {
    // PORTD = closeState;
    TRIGGER(closeState)

  }

}

}


}


void stateMap(int inPin, int outPin){
  triggerState_ = digitalRead(inPin) == HIGH;
  if(triggerState_){
    digitalWrite(outPin, HIGH);
    PORTD  = currentPattern_;
  }else{
    digitalWrite(outPin, LOW);
    PORTD  = closeState;
  }
}


bool waitForSerial(unsigned long timeOut)
{
  unsigned long startTime = millis();
  while (Serial.available() == 0 && (millis() - startTime < timeOut))
  {
  }
  if (Serial.available() > 0)
    return true;
  return false;
}

// Sets analogue output in the TLV5618
// channel is either 0 ('A') or 1 ('B')
// value should be between 0 and 4095 (12 bit max)
// pins should be connected as described above
// void analogueOut(int channel, byte msb, byte lsb)
// {
//   digitalWrite(latchPin, LOW);
//   msb &= B00001111;
//   if (channel == 0)
//     msb |= B10000000;
//   // Note that in all other cases, the data will be written to DAC B and BUFFER
//   shiftOut(dataPin, clockPin, MSBFIRST, msb);
//   shiftOut(dataPin, clockPin, MSBFIRST, lsb);
//   // The TLV5618 needs one more toggle of the clockPin:
//   digitalWrite(clockPin, HIGH);
//   digitalWrite(clockPin, LOW);
//   digitalWrite(latchPin, HIGH);
// }
