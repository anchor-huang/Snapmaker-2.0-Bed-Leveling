#include <Arduino.h>
#include <Wire.h>

/* I2C Bus Slave */
#define I2C_ADDRESS   0x32
#define READ_SENSOR_CMD 0x01
#define INVALID_CMD     0x00

/* Hardware pins */
const uint8_t ledPin =  13;      // the number of the LED pin
const uint8_t clkPin =  10;
const uint8_t dataPin =  8;
const uint8_t readyPin = 1;

/* Constants */
const int ANALOG_READ_RESOLUTION = 8; // Define analog reading 8 bit resolution. Max=256
const int LOGIC_THRESHOLD = 55;    // Define Logic state. Set to High when analog read larger than this value 
const int SIGN_BIT=20;
const int INCH_BIT=23;
unsigned long PATTERN_GAP=10000; // #10 milli second

uint8_t read_logic(uint8_t pin){
    return analogRead(pin)>LOGIC_THRESHOLD? HIGH: LOW;
}

void wait_pattern_start(){
  unsigned long last_faling_edge=micros();
  uint8_t last_value=read_logic(clkPin);
  uint8_t curr_value;
  unsigned long now;

  while(true){
      curr_value=read_logic(clkPin);
      if(last_value==HIGH && curr_value==LOW){   
          now=micros(); 
          if(now-last_faling_edge>PATTERN_GAP){
              break;
          }
      }
      last_value=curr_value;
      last_faling_edge=now;
      delayMicroseconds(20);
  }
}

void wait_clk_rising(){
  uint8_t last_value=read_logic(clkPin);
  uint8_t curr_value;
  while(true){
      curr_value=read_logic(clkPin);
      if(last_value==LOW && curr_value==HIGH){   
          break;
      }
      last_value=curr_value;
      delayMicroseconds(10);
  }
}


int16_t read_dial_indicitor(){
  wait_pattern_start();
  digitalWrite(readyPin, HIGH);
  uint32_t data=0;

  for(uint8_t i=0;i<24;++i){
    // Read 24 bits
    wait_clk_rising();
    bitWrite(data, i, read_logic(dataPin));
  }
  digitalWrite(readyPin, LOW);

  bool is_inch=bitRead(data, INCH_BIT);
  bool is_neg=bitRead(data, SIGN_BIT);
  bitClear(data, INCH_BIT);
  bitClear(data, SIGN_BIT);

  int16_t result=data;
  result=is_inch?result*1.27:result;
  result=is_neg?-result:result; 
  if(is_inch) Serial.println("Inch");
  Serial.println(String("Dial Indictor:")+result);
  return(result);
}

uint8_t  CMD=INVALID_CMD;
uint16_t sensor_result;
boolean  data_ready;

void i2c_handle_receive(int numBytes){
  //Serial.println(String(": OnReceive:")+numBytes);
  if(numBytes>0 and Wire.available()){
      CMD=Wire.read();
      data_ready=false;
      /* Clear Data Ready */
      digitalWrite(readyPin, HIGH);
      //Serial.print("Rec CMD: ");
      //Serial.println(CMD);
  }
}

void i2c_handle_request(){
  uint8_t *buf;
  Serial.println(": OnRequest:");

  if(data_ready){
    buf=(uint8_t*)&sensor_result;
    Serial.print("Response Sensor Read: ");
    Serial.println(sensor_result, HEX);
    
    Wire.write(buf, 2);
  } else {
    Serial.println("Data not ready");
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  pinMode(readyPin, OUTPUT);
  pinMode(clkPin, INPUT);
  pinMode(dataPin, INPUT);
  analogReadResolution(ANALOG_READ_RESOLUTION);

  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(i2c_handle_receive);
  Wire.onRequest(i2c_handle_request);
  CMD=INVALID_CMD;
  digitalWrite(readyPin, HIGH);
  data_ready=false;
}

void loop() {
  // put your main code here, to run repeatedly:
  switch(CMD){
    case READ_SENSOR_CMD:
        sensor_result=read_dial_indicitor();
        digitalWrite(readyPin, LOW);
        data_ready=true;
        CMD=INVALID_CMD;
        break;
    default:
        /* Ignore */
        delay(10);
  }

}