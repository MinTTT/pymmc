/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com
*********/

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define Slave_ADDRESS 0x9
#define SCREEN_ADDRESS 0x3c
// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 Fudisplay(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

float temp = 1.0;
float hum = 1.0;
float set_humidity = 0.0;
float set_temperature = 0.0;
float tempPID = 10.0;
float humPID = 10.0;
char dataBuff[48];
int yshift = 6;

bool reciveData = true;
bool displayNow = true;
void setup() {
  Serial.begin(9600);

  for (;;) {
    if (!Fudisplay.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
      Serial.println("SSD1306 allocation failed.");

    } else {
      Serial.println("SSD1306 allocation Successful.");
      break;
    }
  }
  initialScreen(&Fudisplay, yshift);
  Wire.begin(Slave_ADDRESS);
  Wire.onReceive(receiveEvent);
  delay(1000);



}

void loop() {
  displayTemp(&Fudisplay,
              set_temperature, set_humidity,
              temp, hum, tempPID, humPID,
              yshift);
  delay(100);
    // Serial.print("Humidity: ");
    // Serial.print(hum);
    // Serial.print(" %\t");
    // Serial.print("Temperature: ");
    // Serial.print(temp);
    // Serial.print(" *C\t");
    // Serial.print("Heat_PID: ");
    // Serial.print(tempPID);
    // Serial.print(" \t");
    // Serial.print("Hum_PID: ");
    // Serial.print(humPID);
    // Serial.print(" \n");




}

void receiveEvent() {
  // Data buffer from host device,

  for (int i = 0; i < 48; i++) {
    *(dataBuff + i) = Wire.read();
  }
  convertchar2float((dataBuff + 1 + 8 * 0), &set_humidity);
  convertchar2float((dataBuff + 1 + 8 * 1), &set_temperature);
  convertchar2float((dataBuff + 1 + 8 * 2), &hum);
  convertchar2float((dataBuff + 1 + 8 * 3), &temp);
  convertchar2float((dataBuff + 1 + 8 * 4), &humPID);
  convertchar2float((dataBuff + 1 + 8 * 5), &tempPID);
}

void convertchar2float(char *buff, float *floattemp) {
  String dataString = "";
  char buff2[7];
  for (int i; i < 7; i++) {
    buff2[i] = *(buff + i);
  }
  dataString += buff2;
  *floattemp = dataString.toFloat();
  Serial.println(*floattemp);
}

void initialScreen(Adafruit_SSD1306* display, int shift) {
  display->clearDisplay();
  display->setTextColor(WHITE);
  display->setCursor(0, 20 - shift);
  display->setTextSize(1);
  display->println("Fulab Hum Temp Controller\n V0.01");
  display->display();
}


void displayTemp(Adafruit_SSD1306* display,
                 float tempSV, float humSV,
                 float tempPV, float humPV,
                 float tempPID, float humPID,
                 int yshift) {
  display->clearDisplay();
  display->setTextSize(1);
  display->setTextColor(WHITE);

  // temperature msg
  display->setCursor(0, 15 - yshift);
  display->print("Temperature: ");
  display->setCursor(90, 15 - yshift);
  if(tempPID > 0){
    display->print("0.0");
  }else{
    display->print("X.X");
  }
  // display->println(tempPID, 1);
  display->setCursor(0, 30 - yshift);
  display->print("SV: ");
  display->setCursor(17, 30 - yshift);
  display->println(tempSV, 1);
  display->setCursor(45, 30 - yshift);
  display->cp437(true);
  display->write(167);
  display->print("C");
  display->setCursor(60, 30 - yshift);
  display->print("PV: ");
  display->setCursor(77, 30 - yshift);
  display->println(tempPV, 2);
  display->setCursor(110, 30 - yshift);
  display->cp437(true);
  display->write(167);
  display->print("C");
  // Humidity msg
  display->setCursor(0, 45 - yshift);
  display->print("Humidity: ");
  display->setCursor(90, 45 - yshift);
  // display->println(humPID, 1);
    if(humPID > 0){
    display->print("0.0");
  }else{
    display->print("X.X");
  }
  display->setCursor(0, 60 - yshift);
  display->print("SV: ");
  display->setCursor(17, 60 - yshift);
  display->println(humSV, 1);
  display->setCursor(45, 60 - yshift);
  display->print("%");
  display->setCursor(60, 60 - yshift);
  display->print("PV: ");
  display->setCursor(77, 60 - yshift);
  display->println(humPV, 2);
  display->setCursor(110, 60 - yshift);
  display->print("%");
  display->display();

}
