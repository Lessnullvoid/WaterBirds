int valvPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
int aux;

//- for 12 valves array
//int nValvs = 12;
//- for 8 valves array
int nValvs = 8;


void setup() {
  for (int i=0; i<nValvs; i++){
    pinMode(valvPins[i], OUTPUT);
    digitalWrite(valvPins[i], LOW);
  }
}


void loop() {
  for (int i=0; i<nValvs; i++){
      digitalWrite(valvPins[i], HIGH);
      delay(200);
      digitalWrite(valvPins[i], LOW);
      delay(500);

  }
  delay(8000);

}
