int valvPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
int valvStates[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int aux;
int rdelay = 0;
int delay_between = 10;
int dur1 = 500;
int dur2 = 800;
int dur3 = 500;

unsigned long t0a, t0b;
int ia, ib;
String inputString = "";
bool stringComplete = false;
bool isRunning = false;

//- for 12 valves array
//int nValvs = 12;
//- for 8 valves array
int nValvs = 8;


//- 
void setup() {
  for (int i=0; i<=nValvs; i++){
    pinMode(valvPins[i], OUTPUT);
    digitalWrite(valvPins[i], LOW);
  }
  Serial.begin(115200);
  Serial.println("[waterbirds]");
}


void loop() {

  if (stringComplete) {
    // start running when message ready
    if (inputString=="ready\n"){
      isRunning=true;
      Serial.println("[start]");
      for (int i=0; i<nValvs; i++){    
        digitalWrite(valvPins[i], HIGH);
        delay(50);
        digitalWrite(valvPins[i], LOW);    
      }
    }
    // stop running when message is stop
    if (inputString=="stop\n"){
      isRunning=false;
      Serial.println("[stop]");
      for (int i=nValvs-1; i>=0; i--){    
        digitalWrite(valvPins[i], HIGH);
        delay(50);
        digitalWrite(valvPins[i], LOW);    
      }
    }
    inputString = "";
    stringComplete = false;
  } // end stringComplete if
  
  if (isRunning){
    //for (int i=0; i<nValvs; i++){    
    //pinMode(valvPins[i], OUTPUT);
    int i=analogRead(A1) % nValvs;
    int j=analogRead(A0) % nValvs;
    aux = analogRead(A3);
    aux = aux%32;

    if (aux<10){
      // short chirp
      dur1 = random(240, 750);
      digitalWrite(valvPins[i], HIGH);
      delay(dur1);
      digitalWrite(valvPins[i], LOW);
    } else if(aux<20){
      // large chirp
      dur2 = random(500, 1000);
      digitalWrite(valvPins[i], HIGH);
      delay(dur2);
      digitalWrite(valvPins[i], LOW);      
    } else if(aux<30){
      // double chirp
      dur1 = random(240, 700);
      digitalWrite(valvPins[i], HIGH);
      delay(dur1);
      //int j=analogRead(A0) % nValvs;
      dur2 = random(200, 500);
      digitalWrite(valvPins[j], HIGH);
      delay(dur2);
      digitalWrite(valvPins[i], LOW);          
      dur1 = random(240, 700);
      delay(dur1);
      digitalWrite(valvPins[j], LOW);
    } else {
      delay(10000);
    }    
    delay(4*(dur1+dur2));
  } else {
    for (int i=0; i<nValvs; i++){
      digitalWrite(valvPins[i], LOW);
    }
  }
}


void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
