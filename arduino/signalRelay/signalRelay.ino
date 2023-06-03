

int inputPin = 12;
int outputPin = 13;
boolean triggerState_ = false;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(inputPin, INPUT);
  pinMode(outputPin, OUTPUT);
  delay(100);
}

void loop() {
  // put your main code here, to run repeatedly:
  stateMap(inputPin, outputPin);
}


void stateMap(int inPin, int outPin){
  triggerState_ = digitalRead(inPin) == HIGH;
  if(triggerState_){
    digitalWrite(outPin, HIGH);
  }else{
    digitalWrite(outPin, LOW);
  }
}