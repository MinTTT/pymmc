/**
   @file PID_humidity_control_SHT35.ino
   @author CHU Pan (pan_chu@outlook.com)
   @brief PID control code @ SIAT
   @version 0.1
   @date 2022-10-23

   @copyright Copyright (c) 2022

*/
#include <Wire.h>
#include "Seeed_SHT35.h"
/*SAMD core*/
#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
#define SDAPIN  20
#define SCLPIN  21
#define RSTPIN  7
#define SERIAL SerialUSB
#else
#define SDAPIN  A4
#define SCLPIN  A5
#define RSTPIN  2
#define SERIAL Serial
#define SENSOR_ADDRESS 0x45
#endif
#define Slave_ADDRESS 0x9
#define   ARR_SIZE   10

double values[ARR_SIZE];    // float/doubles are the same on AVR8
int index;

SHT35 sensor(SCLPIN, SENSOR_ADDRESS);

// Display and its parameters

int yshift = 6;

//I/O
int humPWM_pin = 11;  //Pin for PWM signal
int tempPWM_pin = 12; // Pin for temperature

//Variables
float set_humidity = 60.0;
float set_temperature = 30.0;

float Hum_read = 0.0;
float Temp_read = 0.0;

float Hum_corrt = 0.0;
float Temp_corrt = 0;  // SV 30: -1.7  SV 37: -0.2


//PID constants
//////////////////////////////////////////////////////////
int kp =  8000; int ki = 10;  int kd = 85000;
int tempKp = 300; int tempKi = 0;  int tempKd = 18000;
// 20230110 test: int tempKp = 200; int tempKi = 0.;  int tempKd = 5000; int kp = 1000; int ki = 0;  int kd = 8000;
//////////////////////////////////////////////////////////

// PID variables
float tempPIDi = 0;
float tempPIDd = 0.;
float tempPIDerror = 0.;
float tempPIDvalue = 0.;
float humPIDvalue = 0.;
float humPIDerror = 0.;
float humPIDi = 0.;
float humPIDd = 0.;
// Target variables
float timeHum;
float timeTemp;
float timeDisp;
int avgSize = 20;

int updateTime = 500;
// 20230110 test: int updateTime = 500;
char dataBuff[48];

void setup() {
  // Initial sensor
  SERIAL.begin(9600);
  Wire.begin();
  if (sensor.init()) {
    SERIAL.println("Hum & Temp Sensor init failed!!");
  } else {
    SERIAL.println("Hum & Temp Sensor init success!");
  }
  //
  pinMode(tempPWM_pin, OUTPUT);
  pinMode(humPWM_pin, OUTPUT);
  timeHum = millis();
  timeTemp = millis();
  timeDisp = millis();
  delay(1);
}

void loop() {
  Read_serial();
  if (getTempandHum(&Temp_read, &Hum_read, &sensor) == 0) {
    getAvgTempHum(avgSize, &Temp_read, &Hum_read, &sensor);

    //  getAvgTempHum(avgSize, &Temp_read, &Hum_read, &sensor);
    PIDControl(Hum_read, set_humidity, kp, ki, kd,
             &timeHum, &humPIDi, &humPIDerror, &humPIDvalue);
    PIDControl(Temp_read, set_temperature, tempKp, tempKi, tempKd,
             &timeTemp, &tempPIDi, &tempPIDerror, &tempPIDvalue);
    // pid_out_neg(&humPIDvalue, humPWM_pin);
    pid_out_post(&humPIDvalue, humPWM_pin);  // we change a high level trigger to humidifer 2023-05-24.
    pid_out_post(&tempPIDvalue, tempPWM_pin);
  }

  else {
    Serial.println("Sensor READING ERROR");
  }
  if ((millis()-timeDisp) > updateTime){
    transmissionData(set_humidity, set_temperature,
                   Hum_read, Temp_read, humPIDvalue, tempPIDvalue);
    timeDisp = millis();           
  }
  

  // delay(updateTime); //Refresh rate
  //lcd.clear();
}

void transmissionData(float SetHum, float SetTemp,
                      float Hum, float Temp, float HumPID, float TempPID) {
  
  dtostrf(SetHum, 7, 2, (dataBuff + 1 + 8 * 0));
  dtostrf(SetTemp, 7, 2, (dataBuff + 1 + 8 * 1));
  dtostrf(Hum, 7, 2, (dataBuff + 1 + 8 * 2));
  dtostrf(Temp, 7, 2, (dataBuff + 1 + 8 * 3));
  dtostrf(HumPID, 7, 2, (dataBuff + 1 + 8 * 4));
  dtostrf(TempPID, 7, 2, (dataBuff + 1 + 8 * 5));
  Wire.beginTransmission(Slave_ADDRESS); // transmit to device
  for (int i; i < 48; i++) {
    Wire.write(dataBuff[i]);
  }
  Wire.endTransmission();

}


/**
   @brief This function calculates and updates PID value.

   @param CurrentVal current value of controlled parameter.
   @param setVal target value of controlled parameter
   @param kp
   @param ki
   @param kd
   @param[out] ptimePrev
   @param[out] pPID_i
   @param[out] perrorPrev
   @param[out] pPID_value
*/
void PIDControl(const float CurrentVal,
                const float setVal, const int kp, const int ki, const int kd,
                float* ptimePrev, float* pPID_i, float* perrorPrev, float* pPID_value) {
  float error, PID_p, elapsedTime, PID_d;
  error = setVal - CurrentVal;
  PID_p = 0.01 * kp * error;

  elapsedTime = (millis() - *ptimePrev) / 1000;
  *ptimePrev = millis();

  *pPID_i = 0.01 * *pPID_i + (ki * error);
  PID_d = 0.01 * kd * ((error - *perrorPrev) / elapsedTime);


  *perrorPrev = error;
  *pPID_value = PID_p + *pPID_i + PID_d;
}

void pid_out_neg(float* p_pid_v, int Pin) {
  if (*p_pid_v < -255) {
    *p_pid_v = -255;
  }
  if (*p_pid_v  > 255) {
    *p_pid_v = 255;
  }
  if (*p_pid_v > 0) {
    digitalWrite(Pin, LOW);
  }
  else {
    digitalWrite(Pin, HIGH);
  }
}

void pid_hum_control(float* p_pid_hum, float* p_pid_temp, int Pin) {
  if (*p_pid_hum > 0) {
    pid_out_neg(p_pid_hum, Pin);
  } else {
    digitalWrite(Pin, HIGH);
  }
}

void pid_out_post(float* p_pid_v, int Pin) {
  if (*p_pid_v < -255) {
    *p_pid_v  = -255.0;
  }
  if (*p_pid_v  > 255) {
    *p_pid_v  = 255.0;
  }
  if (*p_pid_v > 0.0) {
    digitalWrite(Pin, HIGH);
  }
  else {
    digitalWrite(Pin, LOW);
  }
}

float getHum(SHT35* psensor) {
  float temp, hum;
  getTempandHum(&temp, &hum, psensor);
  return hum;
}

float getTemp(SHT35* psensor) {
  float temp, hum;
  getTempandHum(&temp, &hum, psensor);
  return temp;
}

int getTempandHum(float* pTemp, float* pHum, SHT35* psensor) {
  if (NO_ERROR != psensor->read_meas_data_single_shot(HIGH_REP_WITH_STRCH, pTemp, pHum)) {
    Serial.println("read temp failed!!");
    return -1;
  }
  *pTemp += Temp_corrt;
  *pHum += Hum_corrt;
  return 0;
}


void getAvgTempHum(const int size, float* pTemp, float* pHum, SHT35* psensor) {
  float avgTemp = 0.;
  float avgHum = 0.;
  float tempTemp, tempHum;
  // calculate average temperature and humidity.
  for (int i = 0; i < size; ++i) {
    getTempandHum(&tempTemp, &tempHum, psensor);
    avgHum += tempHum;
    avgTemp += tempTemp;
  }
  avgHum /= size;
  avgTemp /= size;
  *pTemp = avgTemp;
  *pHum = avgHum;
}


// returns true when a new array of values has been
// received and is ready for further processing.
// Otherwise returns false.
/*
    Tx: T   Rcv: Current Temperature
    Rx: H   Rcv: Current Humidity
    Tx: X[value]    Rcv: 1  # set Temperature to [Value]
    Tx: Y[value]    Rcv: 1  # set Humidity to [Value]
*/
bool Read_serial() {
    static bool is_receiving = false;
    while (Serial.available()) {
        String str = Serial.readStringUntil('\n');
        str.trim();
        int str_len = str.length();
        if (str_len == 0) {
            continue;  // Ignore empty lines.
        }
        if (str_len > 0){
              // getAvgTempHum(avgSize, &Temp_read, &Hum_read, &sensor);
              if (str[0] == 'T'){
                Serial.print(Temp_read);
              }
              else if (str[0] == 'H'){
                Serial.print(Hum_read);
              }
              else if (str[0] == 'X'){
                str = str.c_str();
                set_temperature = atof((&str[1]));

              }
              else if (str[0] == 'Y'){
                str = str.c_str();
                set_humidity = atof((&str[1]));
              }
              else if (str[0] == 'M'){
                    // Serial.print("Humidity: ");
                    Serial.print(Hum_read);
                    Serial.print(" ");
                    // Serial.print("Temperature: ");
                    Serial.print(Temp_read);
                    Serial.print(" ");
                    // Serial.print("Heat_PID: ");
                    Serial.print(tempPIDvalue);
                    Serial.print(" ");
                    // Serial.print("Hum_PID: ");
                    Serial.print(humPIDvalue);
                    Serial.print(" ");
                    // Serial.print("TempSV: ");
                    Serial.print(set_temperature);
                    Serial.print(" ");
                    // Serial.print("HumSV: ");
                    Serial.print(set_humidity);
                    Serial.print(" \n");
              }
              return true;
        }
  }
  return false;
}

// // returns true when a new array of values has been
// // received and is ready for further processing.
// // Otherwise returns false.
// bool check_serial() {
//     static bool is_receiving = false;

//     while (Serial.available()) {
//         String str = Serial.readStringUntil('\n');
//         str.trim();

//         if (str.length() == 0) {
//             continue;  // Ignore empty lines.
//         }

//         if (str == "Start") {
//             is_receiving = true;
//             index = 0;
//             continue;
//         }

//         if (is_receiving) {
//             values[index++] = atof(str.c_str());

//             if (index >= ARR_SIZE) {
//                 // We received the final value.
//                 is_receiving = false;  // Reset the flag.
//                 index = 0;
//                 return true;
//             }
//         }
//     }

//     return false;
// }

    


  


// String getValue()