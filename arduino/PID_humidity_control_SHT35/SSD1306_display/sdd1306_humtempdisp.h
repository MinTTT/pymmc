#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Fonts/FreeSerif9pt7b.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define SCREEN_ADDRESS 0x3C // address 
// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);


void initialScreen(Adafruit_SSD1306 display, int shift){
  //  display.setFont(&FreeSerif9pt7b);
  display.clearDisplay();
  display.setTextColor(WHITE);        
  display.setCursor(0,20 - shift);   
  display.setTextSize(1);        
  display.println("Fulab Hum Temp Controller\n V0.01");
  display.display();
}

void displayTemp(Adafruit_SSD1306 display, 
                float tempSV, float humSV, 
                float tempPV, float humPV, 
                int yshift){
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);       
  
  // temperature msg
  display.setCursor(0,15 - yshift);
  display.setTextSize(1); 
  display.print("Temperature: ");
  display.setCursor(0,30 - yshift);
  display.setTextSize(1); 
  display.print("SV: ");
  display.setCursor(17,30 - yshift);
  display.println(tempSV, 1);
  display.setCursor(45, 30 - yshift);
  display.cp437(true);
  display.write(167);
  display.print("C");
  display.setCursor(60,30 - yshift);
  display.print("PV: ");
  display.setCursor(77,30 - yshift);
  display.println(tempPV, 1);
  display.setCursor(110, 30 - yshift);
  display.cp437(true);
  display.write(167);
  display.print("C");
  // Humidity msg
  display.setCursor(0, 45 - yshift);
  display.setTextSize(1);
  display.print("Humidity: ");
  display.setCursor(0, 60 - yshift);
  display.print("SV: ");
  display.setCursor(17,60 - yshift);
  display.println(humSV, 1);
  display.setCursor(45, 60 - yshift);
  display.print("%"); 
  display.setCursor(60,60 - yshift);
  display.print("PV: ");
  display.setCursor(77,60 - yshift);
  display.println(humPV, 1);
  display.setCursor(110, 60 - yshift);
  display.print("%"); 
  display.display();
  
  }