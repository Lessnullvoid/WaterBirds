int valvPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
int aux;
int rdelay = 0;
int delay_between = 10;
int dur1 = 1000;
int dur2 = 1000;
int dur3 = 1000;


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
  for (int i=0; i<nValvs; i++){
    pinMode(valvPins[i], OUTPUT);
    aux = analogRead(A0);
    aux = aux%3;
    if (aux==0){
      // short chirp
      dur1 = random(1500, 3500);
      digitalWrite(valvPins[i], HIGH);
      delay(dur1);
      digitalWrite(valvPins[i], LOW);
    } else if(aux==1){
      // large chirp
      dur2 = random(2000, 3000);
      digitalWrite(valvPins[i], HIGH);
      delay(dur2);
      digitalWrite(valvPins[i], LOW);      
    } else if(aux==2){
      // double chirp
      dur1 = random(1000, 2000);
      digitalWrite(valvPins[i], HIGH);
      delay(dur1);
      int j=analogRead(A0) % nValvs;
      dur2 = random(1000, 2500);
      digitalWrite(valvPins[j], HIGH);
      delay(dur2);
      digitalWrite(valvPins[i], LOW);          
      dur1 = random(1000, 2000);
      delay(dur1);
      digitalWrite(valvPins[j], LOW);
    } else {
      delay(1000);
    }    
  }
  delay(4000);
}
