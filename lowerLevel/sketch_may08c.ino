// подключение библиотек    
#include <Wire.h> // библиотека для работы с I2C датчиком
#include <EEPROM.h> // библиотека для записи в EEPROM
#include <avr/io.h> // библиотека для работы с прерываниями
#include <avr/interrupt.h>

// назначение портов устройств
#define DS1621_ADDRESS 0x48 // адрес датчика температуры
#define lightPin 0 // свет
#define pompPin 7 // помпа
#define lowLevelHumidity 8 // влажность нижний датчик
#define highLevelHumidity 9 // влажность верхний датчик

// переменные состояиния МК, пороги для датчиков
int ID = 0; 
int lightLimit = 0;
int humidityLowLimit = 0;
int humidityHighLimit = 0;
int temperatureLowLimit = 0;
int temperatureHighLimit = 0;
int lightVal = 0;
int lowLevelTemperatureVal = 0;
int highLevelTemperatureVal = 0;
int lowLevelHumidityVal = 0;
int highLevelHumidityVal = 0;
int currentTemperature = -100;
int waitTime = 12;
int tryiedGetWeather = 0;

// переменные для времени
volatile byte SEC = 0;
volatile byte MIN = 0;
volatile byte HOUR = 0;
volatile byte WAKEUP_TIME = 0;
unsigned long timer;

// переменные для определения состояния системы
boolean initialized = false;
boolean needWeather = true;
boolean isWeatherUpdated = false;
boolean wouldBeRain = false;
boolean isPompWorking = false;
boolean isWaiting = false;
boolean needTemperature = false;
boolean waitingTemperature = false;


// первоначальная настройка при включении
void setup() {
  Serial.begin(9600); // настройка соединения по КОМПОРТ
  Wire.begin(); // настройка датчика температуры (I2C)
  Wire.beginTransmission(DS1621_ADDRESS);
  Wire.write(0xAC);
  Wire.write(0);
  Wire.beginTransmission(DS1621_ADDRESS);
  Wire.write(0xEE);
  Wire.endTransmission();
  pinMode(lowLevelHumidity, INPUT); // настройка портов
  pinMode(highLevelHumidity, INPUT);
  pinMode(pompPin, OUTPUT);
  cli(); // настройка таймера на прерывание каждую секунду
  TCCR1A = 0;
  TCCR1B = 0;
  OCR1A = 15624;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS10);
  TCCR1B |= (1 << CS12);
  TIMSK1 |= (1 << OCIE1A);
  sei();
  if (EEPROM.read(0) != 255) { // проверка на наличие инициализации, проверка памяти
    initialized = true;
    ID = EEPROM.read(0); // установка переменных состояния из памяти
    int tmpLight = EEPROM.read(1);
    switch (tmpLight) {
    case 0:
      lightLimit = 1023;
      break;
    case 1:
      lightLimit = 700;
      break;
    case 2:
      lightLimit = 300;
      break;
    case 3:
      lightLimit = 100;
      break;
    }
    temperatureLowLimit = EEPROM.read(2); 
    temperatureHighLimit = EEPROM.read(3);
    humidityLowLimit = EEPROM.read(4);
    humidityHighLimit = EEPROM.read(5);
    waitTime = EEPROM.read(6);
  }
}
// бесконечный цикл
void loop() { 
  if (needTemperature) { // получение температуры
    currentTemperature = getTemperatureValue();
    needTemperature = false;
  }
}

// Обработка прерывания
ISR(TIMER1_COMPA_vect) {
  increaseTime();
  if (Serial.available() > 0) { // проверка входных команд
    char incomingByte;
    int position = 0;
    int message[100];
    while (Serial.available() > 0) {
      incomingByte = Serial.read();
      message[position] = incomingByte - '0';
      position++;
    }
    checkCommands(message, position); // разбор полученной команды
  } else {
    if (needWeather && SEC % 10 == 0) { // отправка запроса на погоду
      if (tryiedGetWeather <= 5) {
        sendWeatherRequest();
      } else {
        tryiedGetWeather = 0;
        isWeatherUpdated = true;
        wouldBeRain = false;
      }
    }
  }
  checkSleep(); // проверка на вывод из режима ожидания
  if (isPompWorking) { // проверка на остановку помпы
    checkStopPomp();
  }
  if (waitingTemperature && currentTemperature != -100) { // проверка на отправку значений датчиков
    sendSensorsValues();
  }
  if (isWeatherUpdated) { // проверка датчиков
    checkSensors();
  }
}
// функция получения температуры с датчика
int16_t get_temperature() { 
  Wire.beginTransmission(DS1621_ADDRESS);
  Wire.write(0xAA);
  Wire.endTransmission(false);
  Wire.requestFrom(DS1621_ADDRESS, 2);
  uint8_t t_msb = Wire.read();
  uint8_t t_lsb = Wire.read();
  int16_t raw_t = (int8_t) t_msb << 1 | t_lsb >> 7;
  raw_t = raw_t * 10 / 2;
  return raw_t;
}
// увеличение времени
void increaseTime() {
  if (SEC == 59) {
    MIN++;
    SEC = 0;
  }
  if (MIN == 59) {
    HOUR++;
    MIN = 0;
  }
  if (HOUR == 23) {
    HOUR = 0;
  }
  SEC++;
}

// попытка инициализации
void tryInitialize(int message[], int position) {
  if (position == 14) {
    initialize(message);
  } else {
    clearBuffer(message);
  }
}

// функция инициализации, запись в EEPROM
void initialize(int message[]) {
  if (message[2] == 0) {
    EEPROM.write(0, message[1]); // ID
    EEPROM.write(1, message[3]); // light
    EEPROM.write(2, message[4] * 10 + message[5]); // temperature lower limit
    EEPROM.write(3, message[6] * 10 + message[7]); // temperature lower limit
    EEPROM.write(4, message[8] * 10 + message[9]); // humidity lower limit
    EEPROM.write(5, message[10] * 10 + message[11]); // humidity upper limit
    EEPROM.write(6, message[12] * 10 + message[13]); // waitTime
    initialized = true;
    char answer[10];
    sprintf(answer, "1%d0", message[1]);
    Serial.println(answer);
    needWeather = true;
  }
}

// функция очистки буфера
void clearBuffer(int message[]) {
  while (Serial.available() > 0) {
    Serial.read();
  }
  memset(message, 0, sizeof(message));
}

// функция проверки датчиков

void checkSensors() {
  boolean lightCondition = checkLightSensor();
  if (lightCondition) {
    boolean temperatureCondition = checkTemperatureSensor();
    if (temperatureCondition && !wouldBeRain) {
      int humidityCondition = checkHumidity();
      if (humidityCondition == 0) {
        startPomp();
      }
    }
  }
}

// функция определения условия освещённости
boolean checkLightSensor() {
  lightVal = analogRead(lightPin);
  return lightVal < lightLimit;
}

// функция получения освещённости
int getLight() {
  lightVal = analogRead(lightPin);
  if (lightVal >= 1023) {
    return 0;
  }
  if (lightVal >= 700) {
    return 1;
  }
  if (lightVal >= 70) {
    return 2;
  }
  return 3;
}

// функция обработки значения датчика
int getTemperatureValue() {
  char c_buffer[8];
  int16_t c_temp = get_temperature();
  if (c_temp < 0) {
    c_temp = abs(c_temp);
    sprintf(c_buffer, "-%2u.%1u", c_temp / 10, c_temp % 10);
  } else {
    if (c_temp >= 1000)
      sprintf(c_buffer, "%3u.%1u", c_temp / 10, c_temp % 10);
    else
      sprintf(c_buffer, " %2u.%1u", c_temp / 10, c_temp % 10);
  }
  return atoi(c_buffer);
}

// функция проверки условия температуры
boolean checkTemperatureSensor() {
  int temperature = getTemperatureValue();
  return temperature > temperatureLowLimit && temperature < temperatureHighLimit;
}

// функция проверки влажности
int checkHumidity() {
  lowLevelHumidityVal = digitalRead(lowLevelHumidity);
  highLevelHumidityVal = digitalRead(highLevelHumidity);
  if (lowLevelHumidityVal == 1) {
    return 0;
  } else if (highLevelHumidityVal == 1) {
    return 1;
  } else {
    return 2;
  }
}

// функция включения помпы
void startPomp() {
  digitalWrite(pompPin, HIGH);
  isPompWorking = true;
}

// функция выключения помпы
void stopPomp() {
  digitalWrite(pompPin, LOW);
  isPompWorking = false;
}

// функция обработки команд
void checkCommands(int message[], int position) {
  if (message[0] == 0 && message[1] == ID) {
    switch (message[2]) {
    case 0:
      tryInitialize(message, position);
      break;
    case 1:
      handleWeather(message, position);
      break;
    case 2:
      handlePomp(message, position);
      break;
    case 3:
      handleSensors(message, position);
      break;
    case 4:
      handleStartCheck(message, position);
    default:
      clearBuffer(message);
      break;
    }
  }
}

// функция отправки запроса на погоду
void sendWeatherRequest() {
  if (SEC % 59 == 0) { // 59
    char request[4];
    sprintf(request, "1%u10", ID);
    Serial.println(request);
  }
}

// функция обработки команды погоды
void handleWeather(int message[], int position) {
  if (position == 4) {
    needWeather = false;
    isWeatherUpdated = true;
    wouldBeRain = message[3];
    char answer[10];
    sprintf(answer, "1%d1%d", ID, wouldBeRain);
    Serial.println(answer);
  } else {
    clearBuffer(message);
  }
}

// проверка условия остановки помпы
void checkStopPomp() {
  if (SEC == 30) {
    int humidityCondition = checkHumidity();
    if (humidityCondition == 2) {
      stopPomp();
      isWaiting = true;
      WAKEUP_TIME = (HOUR + waitTime) % 24;
    }
  }
}

// проверка на выход из режима ожидания
void checkSleep() {
  if (isWaiting && HOUR == WAKEUP_TIME) {
    isWaiting = false;
    needWeather = true;
  }
}

// обработка команд для помпы
void handlePomp(int message[], int position) {
  if (position == 4) {
    switch (message[3]) {
    case 1:
      startPomp();
      break;
    case 0:
      stopPomp();
      break;
    }
    char answer[10];
    sprintf(answer, "1%d2%d", ID, message[3]);
    Serial.println(answer);
  } else {
    clearBuffer(message);
  }
}
// обработка команды отправки значений датчиков
void handleSensors(int message[], int position) {
  if (position == 3) {
    needTemperature = true;
    waitingTemperature = true;
    currentTemperature = -100;
  } else {
    clearBuffer(message);
  }
}

// отправка значений датчиков
void sendSensorsValues() {
  int humidity = checkHumidity();
  int light = getLight();
  char answer[10];
  sprintf(answer, "1%d3%d%d%02d", ID, light, humidity, currentTemperature);
  Serial.println(answer);
  needTemperature = false;
  waitingTemperature = false;
}

// проверка условаия начала цикла проверок 
void checkStartWork() {
  if (MIN == 59 && SEC == 59) {
    needWeather = true;
    isWeatherUpdated = false;
  }
}

// запуск цикла проверок датчиков
void handleStartCheck(int message[], int position) {
   if (position == 3) {
    char answer[10];
    sprintf(answer, "1%d%d", ID, message[2]);
    Serial.println(answer);
    checkSensors();
  } else {
    clearBuffer(message);
  }
}
