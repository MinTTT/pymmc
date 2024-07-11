/*

This script for controling Dyhana Camera, for other type camera, the strategies for controlling camera may change.

*/


#define TicksPerMicroSec 84
#define TicksPerMilliSec 84000
#define pinport PIOB
#define pinmask (0x01 << 27)        // Arduino pin 13 is port B pin 27.
#define triggerMask 0b000111111110  // Arduion pin PC1-8  000111111110  0xFF << 1
#define triggerType 0b000001111110
#define phaseGYMask 0b000110000000
// #define TRIGGER(MAP) PIOC -> PIO_SODR = ((MAP << 1) ^ triggerType)
// #define CLOSE(MAP) PIOC -> PIO_CODR = ((MAP << 1) ^ triggerType)
#define TRIGGER(MAP) PIOC->PIO_ODSR = ((MAP << 1) ^ triggerType)
#define CLOSE PIOC->PIO_ODSR = triggerType
#define GETINPUT PIOD->PIO_PDSR & 0x0040 // D11 PD7 as input
#define TIMEOUT 500
long int t0, t1, lapseTicks, measureTicks, msCount, targetmsCount, TimeTicks, ONTimeTicks, OFFTimeTicks;
long int t_ms;
long int remainTick;
long int stopStick;
long int ONTime = 55000;  // in us
long int OFFTime = 20000;
unsigned long blinkNum = 0;
bool startFlag = true;
bool ONFlag = false;

byte currentPattern_ = 0b10000000;
bool blanking = true;
unsigned long pulseNum = 0;

uint8_t dataBuffer[4];

void setup() {
  PIOB->PIO_OER |= pinmask;
  PIOB->PIO_CODR |= pinmask;    // Turn off the LED
  // PIOD->PIO_ODR = 0xffff;  // set D11 PD7 as input
  pinMode(11, INPUT);
  PIOC->PIO_OER = triggerMask;     // set  D33-D40, PC1-PC8 as output
  CLOSE;
  Serial.begin(9600);
  t_ms = millis();
  msCount = 0;
  t0 = SysTick->VAL;

  ONTimeTicks = ONTime * TicksPerMicroSec;
  OFFTimeTicks = OFFTime * TicksPerMicroSec;
}
void loop() {
  if (Serial.available() > 0) {
    // Serial.println("Read Serial.");
    int inByte = Serial.read();
    switch (inByte) {
      // Set trigger output.
      case 1:
        if (waitForSerial(TIMEOUT)) {
          currentPattern_ = Serial.read();
        }
        break;

      // Get current digital pattern
      case 2:
        Serial.write(byte(2));
        Serial.write(currentPattern_);
        break;

      // out put pulse once
      case 3:
        pulseNum = 1;
        blinkNum = 0;
        startFlag = true;
        break;
      // out put pulse continously
      case 4:
        pulseNum = 0;
        blinkNum = 1;
        startFlag = true;
        break;
      // stop put pulse.
      case 5:
        pulseNum = 0;
        blinkNum = 0;
        startFlag = true;
        pinport->PIO_CODR |= pinmask;
        // Serial.println("Get");
        break;
      case 20:
        blanking = true;
        break;
      case 21:
        blanking = false;
        break;



      // set ON time and OFF time
      case 6:
        // Serial.println("Set Time ON OFF.");
        if (waitForSerial(TIMEOUT)) {
          for (int i = 0; i < 4; i++) {
            waitForSerial(TIMEOUT);
            dataBuffer[i] = Serial.read();
          }
          ONTime = fourBytes2LongInt(dataBuffer);
          for (int i = 0; i < 4; i++) {
            waitForSerial(TIMEOUT);
            dataBuffer[i] = Serial.read();
          }
          OFFTime = fourBytes2LongInt(dataBuffer);

          ONTimeTicks = ONTime * TicksPerMicroSec;
          OFFTimeTicks = OFFTime * TicksPerMicroSec;
        }
        break;
      // start pulase, with fixed loops: (7, loop number)
      case 7:
        if (waitForSerial(TIMEOUT)) {
          for (int i = 0; i < 4; i++) {
            waitForSerial(TIMEOUT);
            dataBuffer[i] = Serial.read();
          }
          pulseNum = fourBytes2LongInt(dataBuffer);
          blinkNum = 0;
          startFlag = true;
        }
    }
  }

  if (pulseNum != blinkNum) {

    // determining the paramters of high and low TTL.
    if (startFlag) {
      // t0 = SysTick->VAL;
      TimeTicks = ONFlag ? ONTimeTicks : OFFTimeTicks;
      remainTick = TimeTicks % TicksPerMilliSec;
      stopStick = (remainTick > t0) ? TicksPerMilliSec - (remainTick - t0) : (t0 - remainTick);
      targetmsCount = (remainTick > t0) ? 1 + TimeTicks / TicksPerMilliSec : TimeTicks / TicksPerMilliSec;
      startFlag = false;
    }
    // if time lapsed over 1 ms, recored it.
    if (SysTick->CTRL & (1 << 16)) {
      msCount++;
    }
    t1 = SysTick->VAL;  // get current tick.
    // Set TTL states.
    if (((t1 <= stopStick) && (msCount >= targetmsCount)) || msCount > targetmsCount) {
      measureTicks = t1;
      startFlag = true;
      lapseTicks = 0;
      msCount = 0;

      if (ONFlag) {
        // pinport->PIO_CODR |= pinmask;  // Turn off the LED
        PIOB->PIO_ODSR = 0x00 << 27;
        t0 = SysTick->VAL;
        ONFlag = false;
        blinkNum++;
      } else {
        PIOB->PIO_ODSR = 0x1 << 27;  // Turn on the LED
        t0 = SysTick->VAL;
        ONFlag = true;
      }
    }
  }


  //
  if (!blanking) {
    // if not in blanking mode, trigger light same as the trigger
    if (ONFlag) {
      TRIGGER(currentPattern_);
    } else {
      // direct close the illumination will let the lines on the bottom of image have less exposure.
      // I set 20 ms delay for closing the illumination
      if (msCount > 20) {
        CLOSE;
      }
    }
  } else {  // blanding mode
    if (PIOD->PIO_PDSR & 0x0080){
      TRIGGER(currentPattern_);
      // Serial.write(PIOD->PIO_PDSR);
    } else {
      CLOSE;
    }
  }

  // // out put blink number
  // if ((millis() - t_ms) >= 1000) {
  //   Serial.print("number of ticks: ");
  //   Serial.print(blinkNum);
  //   Serial.print(";");
  //   Serial.print(pulseNum);
  //   Serial.print(";");
  //   Serial.print(ONTime);
  //   Serial.print(";");
  //   Serial.print(OFFTime);
  //   Serial.println(".");

  //   t_ms = millis();
  // }
}


//wiat the serial.
bool waitForSerial(unsigned long timeOut) {
  unsigned long startTime = millis();
  while (Serial.available() == 0 && (millis() - startTime < timeOut)) {
  }
  if (Serial.available() > 0)
    return true;
  return false;
}

long int fourBytes2LongInt(uint8_t *buffer) {
  long int number;
  number = (long int)buffer[0] << 24
           | (long int)buffer[1] << 16
           | (long int)buffer[2] << 8
           | (long int)buffer[3];
  return number;
}
