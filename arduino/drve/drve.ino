#include <ESP8266WiFi.h>
#include <WiFiUDP.h>
#include <NewPing.h>
#include <ArduinoOTA.h>

#define DEBUG 1

#define TRIG 16
#define ECHO 5
#define MAX_DISTANCE 380
NewPing sonar(TRIG, ECHO, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

#define SPEED1 250
#define SPEED2 400
#define SPEED3 700
#define SPEED4 1000
#define SPEED5 1024
int speed=SPEED1,ii=0;
bool state=0;
int blink=1;
bool us_enabled=true;
#define WL_IDLE_STATUS

const char* ssid = "DRIVE";  //  your network SSID (name)
const char* pass = "nopassword";       // your network password

#define PORT  7777      // local port to listen for UDP packet

WiFiUDP UDP;
char packet[2];
char reply[] = "Packet received!";
char cmd=0;

float duration, distance;
float dist_to_obs()
{
    if (us_enabled ==false){
      return (MAX_DISTANCE);
    }
    duration = sonar.ping();
    distance = (duration / 2) * 0.0343;
#if DEBUG
    Serial.print(" \rD= ");
    Serial.println(distance); // Distance will be 0 when out of set max range.
    
#else
delay(4)
#endif
return distance;
}
#define MOTOR_BP (4)
#define MOTOR_BN (15)
#define MOTOR_FP (2)
#define MOTOR_FN (14)
#define GAS       (13)
#define GEAR      (12)
#define HEAD_LED (0)
#define STOP_DIST (150)



void init_drive(){
    pinMode(MOTOR_BP, OUTPUT);
    analogWrite(MOTOR_BP, 0);
    pinMode(MOTOR_BN, OUTPUT);
    analogWrite(MOTOR_BN, 0);
    pinMode(MOTOR_FP, OUTPUT);
    pinMode(MOTOR_FN, OUTPUT);
    pinMode(HEAD_LED, OUTPUT);
    pinMode(GAS, INPUT_PULLUP);
    pinMode(GEAR, INPUT_PULLUP);
    drive_stop();
    steering_stop();
    
}

void init_wifi(){
  
 WiFi.hostname("car");
#if 0
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
  delay(500);


  }
#endif
  WiFi.softAP("Drive");
  


}
void fwd(){
   blink=0;
    if (dist_to_obs()<STOP_DIST){
    drive_stop();
  
    return;
    //sound horn
  }
 analogWrite(MOTOR_BP, speed);
 analogWrite(MOTOR_BN, 0);
  delay(304);
  drive_stop();
}

void bwd(){
#ifdef BACK_US_SENS
    if (dist_to_obs()<STOP_DIST){
    drive_stop();

    return;
    //sound horn
  }
#endif 
  analogWrite(MOTOR_BP, LOW);
 // digitalWrite(MOTOR_BN, HIGH);
   analogWrite(MOTOR_BN, speed);
  delay(200);
  drive_stop();
}

void left(char withfwd){
   digitalWrite(MOTOR_FP, HIGH);
   digitalWrite(MOTOR_FN, LOW);
   if(withfwd){
    fwd();
   }else{
    delay(300);
   }
     steering_stop();
 
}
void right(char withfwd){
   digitalWrite(MOTOR_FN, HIGH);
   digitalWrite(MOTOR_FP, LOW);
    if(withfwd){
    fwd();
   }else{
    delay(300);
   }
   steering_stop();
}

void steering_stop(){
   digitalWrite(MOTOR_FP, HIGH);
   digitalWrite(MOTOR_FN, HIGH);
 }

void drive_stop(){
 
 #if DEBUG
    Serial.println("drive_stop");
 #endif
 
  analogWrite(MOTOR_BP, 0);
  analogWrite(MOTOR_BN, 0);
  //digitalWrite(MOTOR_BN, LOW);
 }
void  init_ota(){
     ArduinoOTA.setHostname("car");

  // No authentication by default
  // ArduinoOTA.setPassword((const char *)"123");
   ArduinoOTA.setPort(80);
  ArduinoOTA.onStart([]() {
    Serial.println("Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
  });
  ArduinoOTA.begin();
}
void setup()
{
    Serial.begin(115200);
    init_drive();
    init_wifi();
    init_ota();
    UDP.begin(PORT);
    UDP.beginPacket(WiFi.gatewayIP(), UDP.remotePort());
    UDP.write("Connect");
    UDP.endPacket();
    delay(2000);
    right(0);
    delay(300);
    right(0);
    delay(300);
    left(0);
}


void loop()
{
  while(1){
     cmd=0;
      ArduinoOTA.handle();
    if (blink==1){
 
   digitalWrite(HEAD_LED, state);
   state=!state;
   delay(700);
    }


  if(digitalRead(GAS)==LOW){
    
    if(digitalRead(GEAR)==LOW){
      cmd='f';
    }else{
      cmd='b';
    }
  //  Serial.println(cmd);
  }
 
  packet[0]=0;
  int packetSize = UDP.parsePacket();
  if (packetSize>0) {
    int len = UDP.read(packet, 2);
    cmd=packet[0];
     //Serial.println(cmd);
  }if (cmd=='u'){
       us_enabled=!us_enabled;
     for(ii=0;ii<7;ii++){
      digitalWrite(HEAD_LED, state);
      state=!state;
      delay(100);
     }
     continue;
  }
  
  switch(cmd){
    
    case '1':speed=SPEED1;
    break;
    case '2':speed=(SPEED2);
    break;
    case '3':speed=(SPEED3);
    break;
    case '4':speed=(SPEED4);
    break;
    case '5':speed=(SPEED5);
    break;
    case 'f':
      fwd();
    break;
    case 'b':
      bwd();
    break;
    case 'r':
      right(0);
    break;
    case 'l':
      left(0);
    break;
     case 'R':
      right(1);
    break;
    case 'L':
      left(1);
    break;
    case 's':
      drive_stop();
    break;
   
    case 'h':
     blink=0;
      digitalWrite(HEAD_LED, state);
      state=!state;
    break;
  }
   
  }
}
