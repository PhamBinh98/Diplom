from datetime import datetime
from threading import Timer

import matplotlib.pyplot as plt
import requests
import serial
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox

city = input('Введите своё текущее местоположение: ')
API_KEY = '07ee5060141a7b5afe78742de29ea12d'
ser = serial.Serial('COM4', baudrate=9600, timeout=5.0)

night = 'Ночное время'
clouds = 'Пасмурная погода'
day = 'Обычная погода'
everyWeather = 'Очень солнечная погода'
dry = 'Влажность меньше оптимального уровня'
normal = 'Влажность в оптимальных знчениях'
wet = 'Влажность больше или равна максимальному значению'
dateFormat = 'dd/MM/yyyy'

defaultLight = 2
defaultMinTemp = 20
defaultMaxTemp = 30
defaultMinHumidity = 60
defaultMaxHumidity = 70
defaultWaitTime = 6
defaultPhaseEnd = QtCore.QDate.currentDate().addDays(1).toString(dateFormat)
lightValues = [everyWeather, day, clouds, night]
humidityValues = [dry, normal, wet]
newPhase = 'Новая фаза'

defaultPhase = {
    'light': 2,
    'minTemp': defaultMinTemp,
    'maxTemp': defaultMaxTemp,
    'minHumidity': defaultMinHumidity,
    'maxHumidity': defaultMaxHumidity,
    'waitTime': defaultWaitTime,
    'phaseEnd': defaultPhaseEnd
}

emptyCurrentMk = {
    'name': '',
    'id': '',
    'phases': {
        '1': defaultPhase.copy()
    },
    'currentPhase': '1'
}

import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='thanhbinhpham1998',
                             db='system',
                             cursorclass=pymysql.cursors.DictCursor)
print("Подключение к базе данных выполнено успешно")
cursor = connection.cursor()
lat = None
lon = None


try:
    r = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}')
    cityInfo = r.json()[0]
    lat = cityInfo['lat']
    lon = cityInfo['lon']
except Exception as error:
    print(error)


class Ui_MainWindow(object):
    currentMk = emptyCurrentMk
    isCreatingNew = False
    deletedPhases = []
    isWaitingCommand = False

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 500)
        MainWindow.setMinimumSize(QtCore.QSize(500, 500))
        MainWindow.setMaximumSize(QtCore.QSize(500, 500))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mkSelect = QtWidgets.QComboBox(self.centralwidget)
        self.mkSelect.setGeometry(QtCore.QRect(10, 30, 200, 22))
        self.mkSelect.setObjectName("mkSelect")
        self.mkSelectLabel = QtWidgets.QLabel(self.centralwidget)
        self.mkSelectLabel.setGeometry(QtCore.QRect(10, 10, 221, 21))
        self.mkSelectLabel.setObjectName("mkSelectLabel")
        self.addMk = QtWidgets.QPushButton(self.centralwidget)
        self.addMk.setGeometry(QtCore.QRect(10, 60, 200, 31))
        self.addMk.setObjectName("addMk")
        self.light = QtWidgets.QComboBox(self.centralwidget)
        self.light.setGeometry(QtCore.QRect(230, 120, 251, 22))
        self.light.setObjectName("light")
        self.lightLabel = QtWidgets.QLabel(self.centralwidget)
        self.lightLabel.setGeometry(QtCore.QRect(230, 100, 491, 16))
        self.lightLabel.setObjectName("lightLabel")
        self.name = QtWidgets.QLineEdit(self.centralwidget)
        self.name.setGeometry(QtCore.QRect(230, 30, 251, 20))
        self.name.setText("")
        self.name.setObjectName("name")
        self.nameLabel = QtWidgets.QLabel(self.centralwidget)
        self.nameLabel.setGeometry(QtCore.QRect(230, 10, 71, 16))
        self.nameLabel.setObjectName("nameLabel")
        self.humidityLabel = QtWidgets.QLabel(self.centralwidget)
        self.humidityLabel.setGeometry(QtCore.QRect(230, 200, 251, 16))
        self.humidityLabel.setObjectName("humidityLabel")
        self.minHumidity = QtWidgets.QSpinBox(self.centralwidget)
        self.minHumidity.setGeometry(QtCore.QRect(250, 220, 42, 22))
        self.minHumidity.setObjectName("minHumidity")
        self.maxHumidity = QtWidgets.QSpinBox(self.centralwidget)
        self.maxHumidity.setGeometry(QtCore.QRect(320, 220, 42, 22))
        self.maxHumidity.setObjectName("maxHumidity")
        self.minHumidityLabel = QtWidgets.QLabel(self.centralwidget)
        self.minHumidityLabel.setGeometry(QtCore.QRect(230, 220, 51, 21))
        self.minHumidityLabel.setObjectName("minHumidityLabel")
        self.maxHumidityLabel = QtWidgets.QLabel(self.centralwidget)
        self.maxHumidityLabel.setGeometry(QtCore.QRect(300, 220, 47, 21))
        self.maxHumidityLabel.setObjectName("maxHumidityLabel")
        self.maxTempLabel = QtWidgets.QLabel(self.centralwidget)
        self.maxTempLabel.setGeometry(QtCore.QRect(300, 170, 47, 21))
        self.maxTempLabel.setObjectName("maxTempLabel")
        self.maxTemp = QtWidgets.QSpinBox(self.centralwidget)
        self.maxTemp.setGeometry(QtCore.QRect(320, 170, 42, 22))
        self.maxTemp.setObjectName("maxTemp")
        self.minTemp = QtWidgets.QSpinBox(self.centralwidget)
        self.minTemp.setGeometry(QtCore.QRect(250, 170, 42, 22))
        self.minTemp.setObjectName("minTemp")
        self.minTempLabel = QtWidgets.QLabel(self.centralwidget)
        self.minTempLabel.setGeometry(QtCore.QRect(230, 170, 51, 21))
        self.minTempLabel.setObjectName("minTempLabel")
        self.tempLabel = QtWidgets.QLabel(self.centralwidget)
        self.tempLabel.setGeometry(QtCore.QRect(230, 150, 251, 16))
        self.tempLabel.setObjectName("tempLabel")
        self.waitTime = QtWidgets.QSpinBox(self.centralwidget)
        self.waitTime.setGeometry(QtCore.QRect(230, 270, 42, 22))
        self.waitTime.setObjectName("waitTime")
        self.waitTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.waitTimeLabel.setGeometry(QtCore.QRect(230, 250, 261, 16))
        self.waitTimeLabel.setObjectName("waitTimeLabel")
        self.phaseEnd = QtWidgets.QDateEdit(self.centralwidget)
        self.phaseEnd.setGeometry(QtCore.QRect(230, 320, 110, 22))
        self.phaseEnd.setObjectName("phaseEnd")
        self.phaseEndLabel = QtWidgets.QLabel(self.centralwidget)
        self.phaseEndLabel.setGeometry(QtCore.QRect(230, 300, 261, 16))
        self.phaseEndLabel.setObjectName("phaseEndLabel")
        self.stageNumberLabel = QtWidgets.QLabel(self.centralwidget)
        self.stageNumberLabel.setGeometry(QtCore.QRect(230, 60, 251, 16))
        self.stageNumberLabel.setObjectName("stageNumberLabel")
        self.addPhase = QtWidgets.QPushButton(self.centralwidget)
        self.addPhase.setGeometry(QtCore.QRect(230, 360, 251, 23))
        self.addPhase.setObjectName("addPhase")
        self.stageNumber = QtWidgets.QComboBox(self.centralwidget)
        self.stageNumber.setGeometry(QtCore.QRect(230, 80, 251, 22))
        self.stageNumber.setObjectName("stageNumber")
        self.deleteMk = QtWidgets.QPushButton(self.centralwidget)
        self.deleteMk.setGeometry(QtCore.QRect(10, 140, 200, 31))
        self.deleteMk.setObjectName("deleteMk")
        self.saveMk = QtWidgets.QPushButton(self.centralwidget)
        self.saveMk.setGeometry(QtCore.QRect(10, 60, 200, 31))
        self.saveMk.setObjectName("saveMk")
        self.deletePhase = QtWidgets.QPushButton(self.centralwidget)
        self.deletePhase.setGeometry(QtCore.QRect(230, 400, 251, 23))
        self.deletePhase.setObjectName("deletePhase")
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(10, 180, 200, 31))
        self.start.setObjectName("start")
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setGeometry(QtCore.QRect(10, 220, 200, 31))
        self.stop.setObjectName("stop")
        self.startCheck = QtWidgets.QPushButton(self.centralwidget)
        self.startCheck.setGeometry(QtCore.QRect(10, 260, 200, 31))
        self.startCheck.setObjectName("startCheck")
        self.getSensors = QtWidgets.QPushButton(self.centralwidget)
        self.getSensors.setGeometry(QtCore.QRect(10, 300, 200, 31))
        self.getSensors.setObjectName("getSensors")
        self.statsLabel = QtWidgets.QPushButton(self.centralwidget)
        self.statsLabel.setGeometry(QtCore.QRect(10, 340, 200, 31))
        self.statsLabel.setObjectName("statsLabel")
        self.fromStats = QtWidgets.QDateEdit(self.centralwidget)
        self.fromStats.setGeometry(QtCore.QRect(30, 390, 100, 22))
        self.fromStats.setObjectName("fromStats")
        self.toStats = QtWidgets.QDateEdit(self.centralwidget)
        self.toStats.setGeometry(QtCore.QRect(30, 420, 100, 22))
        self.toStats.setObjectName("toStats")
        self.fromStatsLabel = QtWidgets.QLabel(self.centralwidget)
        self.fromStatsLabel.setGeometry(QtCore.QRect(10, 390, 51, 21))
        self.fromStatsLabel.setObjectName("fromStatsLabel")
        self.toStatsLabel = QtWidgets.QLabel(self.centralwidget)
        self.toStatsLabel.setGeometry(QtCore.QRect(10, 420, 47, 21))
        self.toStatsLabel.setObjectName("toStatsLabel")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.getMkList()
        self.addFunctions()
        self.light.addItems(lightValues)
        self.checkIncomingCommands()
        self.checkChangePhases()
        self.getStats()
        self.startWateringCheck()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Управление системой полива"))
        self.mkSelectLabel.setText(_translate("MainWindow", "Выберите микроконтроллер"))
        self.addMk.setText(_translate("MainWindow", "Добавить микроконтроллер"))
        self.lightLabel.setText(_translate("MainWindow", "Оптимальная освещённость"))
        self.nameLabel.setText(_translate("MainWindow", "Название"))
        self.humidityLabel.setText(_translate("MainWindow", "Оптимальная влажность(%)"))
        self.minHumidityLabel.setText(_translate("MainWindow", "От"))
        self.maxHumidityLabel.setText(_translate("MainWindow", "до"))
        self.maxTempLabel.setText(_translate("MainWindow", "до"))
        self.minTempLabel.setText(_translate("MainWindow", "От"))
        self.tempLabel.setText(_translate("MainWindow", "Оптимальная температура(℃)"))
        self.waitTimeLabel.setText(_translate("MainWindow", "Время ожидания между поливами(часы)"))
        self.phaseEndLabel.setText(_translate("MainWindow", "Дата завершения фазы"))
        self.stageNumberLabel.setText(_translate("MainWindow", "Номер фазы"))
        self.addPhase.setText(_translate("MainWindow", "Добавить фазу роста"))
        self.deleteMk.setText(_translate("MainWindow", "Удалить микроконтроллер"))
        self.saveMk.setText(_translate("MainWindow", "Сохранить микроконтроллер"))
        self.deletePhase.setText(_translate("MainWindow", "Удалить фазу роста"))
        self.start.setText(_translate("MainWindow", "Включить полив"))
        self.stop.setText(_translate("MainWindow", "Выключить полив"))
        self.startCheck.setText(_translate("MainWindow", "Запустить цикл проверок"))
        self.getSensors.setText(_translate("MainWindow", "Получить значения датчиков"))
        self.statsLabel.setText(_translate("MainWindow", "Запросить статистику"))
        self.fromStatsLabel.setText(_translate("MainWindow", "от"))
        self.toStatsLabel.setText(_translate("MainWindow", "до"))

    def addFunctions(self):
        self.initComponents()
        self.addMk.clicked.connect(self.handleAddMk)
        self.name.textEdited.connect(lambda: self.handleChange(self.name.displayText(), 'name'))
        self.light.currentIndexChanged.connect(lambda: self.handleChange(self.light.currentIndex(), 'light'))
        self.minTemp.valueChanged.connect(lambda: self.handleChange(self.minTemp.value(), 'minTemp'))
        self.maxTemp.valueChanged.connect(lambda: self.handleChange(self.maxTemp.value(), 'maxTemp'))
        self.minHumidity.valueChanged.connect(lambda: self.handleChange(self.minHumidity.value(), 'minHumidity'))
        self.maxHumidity.valueChanged.connect(lambda: self.handleChange(self.maxHumidity.value(), 'maxHumidity'))
        self.waitTime.valueChanged.connect(lambda: self.handleChange(self.waitTime.value(), 'waitTime'))
        self.phaseEnd.dateChanged.connect(lambda: self.handleChange(self.phaseEnd.date(), 'phaseEnd'))
        self.addPhase.clicked.connect(self.handleAddPhase)
        self.stageNumber.currentIndexChanged.connect(self.handleStageNumberChanged)
        self.deletePhase.clicked.connect(self.handleDeletePhase)
        self.mkSelect.currentIndexChanged.connect(self.handleChangeMk)
        self.saveMk.clicked.connect(self.handleSaveMk)
        self.deleteMk.clicked.connect(self.handleDeleteMk)
        self.start.clicked.connect(self.handleStart)
        self.stop.clicked.connect(self.handleStop)
        self.startCheck.clicked.connect(self.handleStartCheck)
        self.getSensors.clicked.connect(self.handleSensors)
        self.statsLabel.clicked.connect(self.handleGetStats)

    def initComponents(self):
        if self.mkSelect.count() == 0:
            self.hideMainElements()
        else:
            self.showMainElements()
        self.minTemp.setMinimum(-20)
        self.minTemp.setMaximum(50)
        self.maxTemp.setMinimum(-20)
        self.maxTemp.setMaximum(50)
        self.minHumidity.setMinimum(0)
        self.minHumidity.setMaximum(100)
        self.maxHumidity.setMinimum(0)
        self.maxHumidity.setMaximum(100)
        self.waitTime.setMinimum(1)
        self.waitTime.setMaximum(24)
        self.phaseEnd.setMinimumDate(QtCore.QDate.currentDate())
        self.phaseEnd.setMaximumDate(QtCore.QDate.currentDate().addYears(1))
        self.fromStats.setDate(QtCore.QDate.currentDate())
        self.toStats.setDate(QtCore.QDate.currentDate())

    def handleAddMk(self):
        try:
            self.addMk.hide()
            self.saveMk.show()
            self.name.show()
            self.nameLabel.show()
            self.phaseEnd.show()
            self.phaseEndLabel.show()
            self.stageNumber.show()
            self.stageNumberLabel.show()
            self.light.show()
            self.lightLabel.show()
            self.tempLabel.show()
            self.maxTemp.show()
            self.maxTempLabel.show()
            self.minTemp.show()
            self.minTempLabel.show()
            self.humidityLabel.show()
            self.minHumidity.show()
            self.minHumidityLabel.show()
            self.maxHumidity.show()
            self.maxHumidityLabel.show()
            self.addPhase.show()
            self.waitTime.show()
            self.waitTimeLabel.show()
            self.stageNumber.clear()
            self.stageNumber.addItem('1')
            self.isCreatingNew = True
            self.mkSelect.addItem(str(self.mkSelect.count()))
            self.mkSelect.setCurrentIndex(self.mkSelect.count() - 1)
            self.name.setText(str(self.mkSelect.count() - 1))
            self.light.setCurrentIndex(defaultLight)
            self.minTemp.setValue(defaultMinTemp)
            self.maxTemp.setValue(defaultMaxTemp)
            self.minHumidity.setValue(defaultMinHumidity)
            self.maxHumidity.setValue(defaultMaxHumidity)
            self.waitTime.setValue(defaultWaitTime)
            self.deleteMk.hide()
            self.saveMk.show()
            self.start.hide()
            self.stop.hide()
            self.startCheck.hide()
            self.getSensors.hide()
            self.statsLabel.hide()
            self.fromStats.hide()
            self.fromStatsLabel.hide()
            self.toStats.hide()
            self.toStatsLabel.hide()
            self.addMk.hide()
            self.addMk.setGeometry(QtCore.QRect(10, 100, 200, 31))
        except Exception as error:
            self.getPopUp('Ошибка', str(error))

    def handleChange(self, value, key):
        currentPhase = str(self.currentMk['currentPhase'])
        if key == 'name':
            self.currentMk[key] = value
            index = self.mkSelect.currentIndex()
            self.mkSelect.setItemText(index, value)
        else:
            self.currentMk['phases'][currentPhase][key] = value.toString(
                dateFormat) if key == 'phaseEnd' else value

    def handleAddPhase(self):
        phasesLen = len(self.currentMk['phases'].keys())
        self.currentMk['phases'][str(phasesLen + 1)] = defaultPhase.copy()
        self.stageNumber.addItem(str(phasesLen + 1))
        self.stageNumber.setCurrentIndex(phasesLen)

    def handleStageNumberChanged(self, newIndex):
        if newIndex != -1:
            currentPhase = self.currentMk['phases'][str(newIndex + 1)]
            self.currentMk['currentPhase'] = str(newIndex + 1)
            self.light.setCurrentIndex(currentPhase['light'])
            self.minTemp.setValue(currentPhase['minTemp'])
            self.maxTemp.setValue(currentPhase['maxTemp'])
            self.minHumidity.setValue(currentPhase['minHumidity'])
            self.maxHumidity.setValue(currentPhase['maxHumidity'])
            self.waitTime.setValue(currentPhase['waitTime'])
            self.phaseEnd.setDate(QtCore.QDate.fromString(currentPhase['phaseEnd'], dateFormat))
            if self.stageNumber.count() != 1:
                self.deletePhase.show()
            else:
                self.deletePhase.hide()

    def handleDeletePhase(self):
        currentPhase = self.currentMk['currentPhase']
        self.deletedPhases.append(self.currentMk['currentPhase'])
        del self.currentMk['phases'][currentPhase]
        self.stageNumber.removeItem(int(currentPhase) - 1)

    def getMkList(self):
        try:
            sql = """SELECT * FROM microcontrollers"""
            cursor.execute(sql)
            connection.commit()
            if cursor.rowcount != 0:
                for row in cursor:
                    self.mkSelect.addItem(row['name'])
                currentIndex = self.mkSelect.count() - 1
                if currentIndex != -1:
                    self.handleChangeMk(currentIndex)
        except connection.Error as error:
            self.getPopUp('Ошибка', str(error))

    def handleChangeMk(self, newIndex):
        if not self.isCreatingNew and newIndex != -1:
            self.name.setText(self.mkSelect.currentText())
            try:
                mkSql = """SELECT * FROM phases WHERE mkId=%s"""
                cursor.execute(mkSql, newIndex)
                connection.commit()
                self.currentMk['phases'] = {}
                isCurrentPhaseSet = False
                self.stageNumber.clear()
                for row in cursor:
                    if not isCurrentPhaseSet:
                        self.currentMk['currentPhase'] = row['phaseNumber']
                        isCurrentPhaseSet = True
                    self.stageNumber.addItem(str(row['phaseNumber']))
                    self.currentMk['phases'][str(row['phaseNumber'])] = {
                        'id': row['id'],
                        'light': row['light'],
                        'minTemp': row['minTemp'],
                        'maxTemp': row['maxTemp'],
                        'minHumidity': row['minHumidity'],
                        'maxHumidity': row['maxHumidity'],
                        'waitTime': row['waitTime'],
                        'phaseEnd': row['phaseEnd']
                    }
                try:
                    currentPhase = self.currentMk['phases'][str(self.currentMk['currentPhase'])]
                    self.light.setCurrentIndex(currentPhase['light'])
                    self.minTemp.setValue(currentPhase['minTemp'])
                    self.maxTemp.setValue(currentPhase['maxTemp'])
                    self.minHumidity.setValue(currentPhase['minHumidity'])
                    self.maxHumidity.setValue(currentPhase['maxHumidity'])
                    self.waitTime.setValue(currentPhase['waitTime'])
                except Exception:
                    self.getPopUp('Внимание',
                                  f"Похоже микроконтроллер {self.mkSelect.currentIndex()}-{self.mkSelect.currentText()} "
                                  f"отработал все фазы \nБудет произведено удаление из системы")
                    self.handleDeleteMk()

            except connection.Error as error:
                self.getPopUp('Ошибка', str(error))
            self.showMainElements()
        else:
            self.isCreatingNew = False
        self.initComponents()

    def handleSaveMk(self):
        try:
            mkIndex = self.mkSelect.currentIndex()
            if len(self.deletedPhases) != 0:
                delPhaseSql = """DELETE FROM phases WHERE mkId=%s and phaseNumber in %s"""
                cursor.execute(delPhaseSql, (mkIndex, self.deletedPhases))
                connection.commit()
                self.deletedPhases = []
            mkSql = """INSERT INTO microcontrollers (id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE id=%s, name=%s"""
            mkValues = (mkIndex, self.mkSelect.currentText(), mkIndex, self.mkSelect.currentText())
            cursor.execute(mkSql, mkValues)
            connection.commit()
            phasesValues = []
            phasesUpdates = []
            for id, values in self.currentMk['phases'].items():
                if 'id' not in values.keys():
                    phasesValues.append((
                        mkIndex, int(id), values['light'], values['minTemp'], values['maxTemp'], values['minHumidity'],
                        values['maxHumidity'], values['waitTime'], values['phaseEnd']))
                else:
                    phasesUpdates.append((
                        int(id), values['light'], values['minTemp'], values['maxTemp'],
                        values['minHumidity'],
                        values['maxHumidity'], values['waitTime'], values['phaseEnd'], values['id'])
                    )
            if len(phasesValues) != 0:
                phasesSql = """INSERT INTO phases (mkId, phaseNumber, light, minTemp, maxTemp, minHumidity,maxHumidity,
                waitTime,phaseEnd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.executemany(phasesSql, phasesValues)
                connection.commit()
            if len(phasesUpdates) != 0:
                for values in phasesUpdates:
                    updatesSql = """UPDATE phases SET phaseNumber=%s, light=%s, minTemp=%s, maxTemp=%s, minHumidity=%s,
                    maxHumidity=%s, waitTime=%s, phaseEnd=%s WHERE id=%s"""
                    cursor.execute(updatesSql, values)
                    connection.commit()
            self.deleteMk.show()
            self.saveMk.show()
            self.start.show()
            self.stop.show()
            self.startCheck.show()
            self.getSensors.show()
            self.statsLabel.show()
            self.fromStats.show()
            self.fromStatsLabel.show()
            self.toStats.show()
            self.toStatsLabel.show()
            self.addMk.show()
            self.addMk.setGeometry(QtCore.QRect(10, 100, 200, 31))
            activePhase = None
            activeId = None
            currentDate = QtCore.QDate.currentDate().toString(dateFormat)
            for id, phase in list(self.currentMk['phases'].items()):
                if phase['phaseEnd'] > currentDate:
                    activePhase = phase
                    activeId = id
                    break
            if activePhase and activeId:
                sql = """SELECT * FROM phases WHERE phaseNumber=%s AND light=%s AND minTemp=%s AND maxTemp=%s AND 
                minHumidity=%s AND maxHumidity=%s AND waitTime=%s AND phaseEnd=%s AND mkId=%s """
                values = (int(activeId), activePhase['light'], activePhase['minTemp'], activePhase['maxTemp'],
                          activePhase['minHumidity'], activePhase['maxHumidity'], activePhase['waitTime'],
                          activePhase['phaseEnd'], mkIndex)
                cursor.execute(sql, values)
                connection.commit()
                phaseId = None
                if cursor.rowcount != 0:
                    for row in cursor:
                        phaseId = row['id']
                        break
                    sql = """INSERT INTO currentPhases (mkId, phaseId) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mkId=%s, phaseId=%s"""
                    cursor.execute(sql, (mkIndex, phaseId, mkIndex, phaseId))
                    connection.commit()
                    command = f"0{mkIndex}0{activePhase['light']}{activePhase['minTemp']:02d}{activePhase['maxTemp']:02d}" \
                              f"{activePhase['minHumidity']:02d}{activePhase['maxHumidity']:02d}{activePhase['waitTime']:02d}"
                    answer = f"1{mkIndex}0\r\n"
                    self.sendToMk(0, command.encode('ascii'), answer, "Микроконтроллер успешно проинициализирован")
                else:
                    self.getPopUp('Ошибка', "Произошла ошибка базы данных, удалите данный микроконтроллер и создайте "
                                            "заново")

        except connection.Error as error:
            self.getPopUp('Ошибка', str(error))

    def handleDeleteMk(self):
        try:
            index = self.mkSelect.currentIndex()
            sql = """DELETE FROM microcontrollers WHERE id=%s"""
            cursor.execute(sql, index)
            connection.commit()
            self.mkSelect.removeItem(index)
        except connection.Error as error:
            self.getPopUp('Ошибка', str(error))

    def getWeather(self):
        try:
            r = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}')
            result = r.json()
            weather = result['weather'][0]
            wouldBeRain = 'rain' in weather['main'].lower()
            return 1 if wouldBeRain else 0

        except Exception as error:
            self.getPopUp('Ошибка', str(error))

    def sendToMk(self, count, command, answer, successMsg=None, commandType=None, noPopup=False):
        self.isWaitingCommand = True
        try:
            if count < 5:
                ser.write(command)
                try:
                    result = ser.read(size=len(answer)).decode('utf-8')
                    res = result.replace('\r\n', '')
                    ans = answer.replace('\r\n', '')
                    if not res:
                        print(f'Не было получено ответа, переотправляю команду - {command}, попытка {count + 1}')
                        self.sendToMk(count + 1, command, answer, successMsg, commandType)
                    if not commandType:
                        if result == answer:
                            if successMsg:
                                if not noPopup:
                                    self.getPopUp("Выполнено", successMsg)
                                self.isWaitingCommand = False
                            else:
                                print('Команда выполнена')
                        else:
                            print(f"Полученный ответ {res} отличается от ожидаемого {ans}, переотправляю команду")
                            self.sendToMk(count + 1, command, answer, successMsg)
                    else:
                        if commandType == 3:
                            light = lightValues[int(res[3])]
                            humidity = humidityValues[int(res[4])]
                            temp = res[5:]
                            self.isWaitingCommand = False
                            if not noPopup:
                                self.getPopUp("Выполнено",
                                              f'Получены следующие значения датчиков:\nОсвещённость: {light}\nВлажность: {humidity}\nТемпература: {temp}')
                            mkId = int(chr(command[1]))
                            sql = """INSERT INTO stats (mkId, day, time, temp, humidity, light) VALUES (%s, %s, %s, %s, %s, %s)"""
                            day = QtCore.QDate.currentDate().toString(dateFormat)
                            time = datetime.now().strftime("%H:%M")
                            values = (mkId, day, time, temp, int(res[4]), int(res[3]))
                            cursor.execute(sql, values)
                            connection.commit()
                except serial.SerialTimeoutException:
                    print(f"Не удалось связать с микроконтроллером, попытка {count + 1}")
                    self.sendToMk(count + 1, command, answer, successMsg)
            else:
                self.getPopUp('Ошибка', 'Не удалось установить связь с микроконтроллером')
        except Exception as error:
            self.getPopUp('Ошибка', str(error))

    def handleStart(self):
        mkIndex = self.mkSelect.currentIndex()
        command = f"0{mkIndex}21"
        answer = f"1{mkIndex}21\r\n"
        self.sendToMk(0, command.encode('ascii'), answer, "Помпа включена")

    def handleStop(self):
        mkIndex = self.mkSelect.currentIndex()
        command = f"0{mkIndex}20"
        answer = f"1{mkIndex}20\r\n"
        self.sendToMk(0, command.encode('ascii'), answer, "Помпа выключена")

    def handleStartCheck(self, mkId=None, noPopup=False):
        mkIndex = mkId if mkId else self.mkSelect.currentIndex()
        command = f"0{mkIndex}4"
        answer = f"1{mkIndex}4\r\n"
        self.sendToMk(0, command.encode('ascii'), answer, "Проверка датчиков успешно запущена", noPopup=noPopup)

    def handleSensors(self, mkId=None, noPopup=False):
        mkIndex = mkId if mkId else self.mkSelect.currentIndex()
        command = f"0{mkIndex}3"
        answer = f"0000000\r\n"
        self.sendToMk(0, command.encode('ascii'), answer, commandType=3, noPopup=noPopup)

    def checkIncomingCommands(self):
        if not self.isWaitingCommand:
            waitingBytes = ser.inWaiting()
            if waitingBytes != 0:
                data = ser.read(waitingBytes).decode('utf-8').split('\r\n')
                haveRain = self.getWeather()
                for command in data:
                    if len(command) >= 3:
                        dir = command[0]
                        if dir == '1':
                            id = command[1]
                            commandType = command[2]
                            if commandType == '1':
                                newCommand = f"0{id}1{haveRain}"
                                answer = f"1{id}1{haveRain}\r\n"
                                self.sendToMk(0, newCommand.encode('ascii'), answer)
                            else:
                                print(f'Команда {command} не является исполняемой верхним уровнем')
                        else:
                            print(f'Неверный формат команды - {command}')

        Timer(10, self.checkIncomingCommands).start()

    def checkChangePhases(self):
        currentDate = QtCore.QDate.currentDate().toString(dateFormat)
        try:
            sql = """SELECT * FROM microcontrollers"""
            cursor.execute(sql)
            connection.commit()
            mkIds = []
            currentPhases = {}
            if cursor.rowcount != 0:
                for row in cursor:
                    mkIds.append(row['id'])
            sql = """SELECT * FROM currentPhases"""
            cursor.execute(sql)
            connection.commit()
            if cursor.rowcount != 0:
                for row in cursor:
                    currentPhases[row['mkId']] = row['phaseId']
            for id in mkIds:
                sql = """SELECT * FROM phases WHERE mkId=%s"""
                cursor.execute(sql, id)
                connection.commit()
                currentPhase = None
                shouldBeNext = None
                if cursor.rowcount != 0:
                    for row in cursor:
                        if row['id'] == currentPhases[id]:
                            currentPhase = row
                        if row['phaseEnd'] > currentDate and shouldBeNext == None:
                            shouldBeNext = row
                    if not shouldBeNext:
                        self.getPopUp('Предупреждение', f"микроконтроллер {id} отработал все свои фазы")
                    else:
                        if shouldBeNext['id'] != currentPhase['id']:
                            sql = """INSERT INTO currentPhases (mkId, phaseId) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mkId=%s, phaseId=%s"""
                            cursor.execute(sql, (id, currentPhases[id], id, currentPhases[id]))
                            connection.commit()
                            command = f"0{id}0{shouldBeNext['light']}{shouldBeNext['minTemp']:02d}{shouldBeNext['maxTemp']:02d}" \
                                      f"{shouldBeNext['minHumidity']:02d}{shouldBeNext['maxHumidity']:02d}{shouldBeNext['waitTime']:02d}"
                            answer = f"1{id}0\r\n"
                            self.sendToMk(0, command.encode('ascii'), answer,
                                          "Микроконтроллер успешно проинициализирован")
        except Exception as error:
            self.getPopUp('Ошибка', str(error))
        Timer(86400, self.checkIncomingCommands).start()

    def getStats(self):
        sql = """SELECT * FROM microcontrollers"""
        cursor.execute(sql)
        connection.commit()
        mkIds = []
        if cursor.rowcount != 0:
            for row in cursor:
                mkIds.append(row['id'])
        for id in mkIds:
            self.handleSensors(mkId=id, noPopup=True)
        Timer(3600, self.getStats).start()

    def handleGetStats(self):
        try:
            mkIndex = self.mkSelect.currentIndex()
            statsFrom = self.fromStats.date().toString(dateFormat)
            statsTo = self.toStats.date().toString(dateFormat)
            sql = """SELECT * FROM stats WHERE mkId=%s AND day <= %s AND day >= %s"""
            cursor.execute(sql, (mkIndex, statsFrom, statsTo))
            connection.commit()
            time = []
            light = []
            humidity = []
            temp = []
            if cursor.rowcount != 0:
                for row in cursor:
                    temp.append(row['temp'])
                    light.append(row['light'])
                    humidity.append(row['humidity'])
                    statTime = datetime.strptime(f"{row['day']} {row['time']}", '%d/%m/%Y %H:%M')
                    time.append(statTime)
                self.getGraphic(time, temp, 'temp')
                self.getGraphic(time, light, 'light')
                self.getGraphic(time, humidity, 'humidity')
            else:
                self.getPopUp('Предупрждение', "Для данного микроконтроллера статистика пока что не доступна")
        except Exception as error:
            self.getPopUp('Ошибка', str(error))

    def getGraphic(self, xData, yData, type):
        xLabel = "Время"
        yLabel = ""
        if type == 'temp':
            yLabel = "Температура"
        elif type == 'light':
            yLabel = "Освещённость"
        elif type == 'humidity':
            yLabel = "Уровень влажности"
        plt.figure(figsize=(12, 7))
        plt.plot(xData, yData)
        plt.xlabel(xLabel)
        plt.ylabel(yLabel)
        plt.legend()
        plt.show()

    def startWateringCheck(self):
        currentTime = datetime.now()
        hour = currentTime.hour
        minute = currentTime.minute
        if (hour == 18 or hour == 6) and minute < 10:
            sql = """SELECT * FROM microcontrollers"""
            cursor.execute(sql)
            connection.commit()
            mkIds = []
            if cursor.rowcount != 0:
                for row in cursor:
                    mkIds.append(row['id'])
            for id in mkIds:
                self.handleStartCheck(mkId=id, noPopup=True)
            Timer(43200, self.getStats).start()
        else:
            targetTime = 18 * 3600 if hour > 6 else 6 * 3600
            diff = abs(targetTime - (hour * 3600 + 60 * minute))
            Timer(diff, self.getStats).start()

    def hideMainElements(self):
        self.deleteMk.hide()
        self.saveMk.hide()
        self.start.hide()
        self.stop.hide()
        self.startCheck.hide()
        self.getSensors.hide()
        self.name.hide()
        self.nameLabel.hide()
        self.phaseEnd.hide()
        self.phaseEndLabel.hide()
        self.stageNumber.hide()
        self.stageNumberLabel.hide()
        self.light.hide()
        self.lightLabel.hide()
        self.tempLabel.hide()
        self.maxTemp.hide()
        self.maxTempLabel.hide()
        self.minTemp.hide()
        self.minTempLabel.hide()
        self.humidityLabel.hide()
        self.minHumidity.hide()
        self.minHumidityLabel.hide()
        self.maxHumidity.hide()
        self.maxHumidityLabel.hide()
        self.addPhase.hide()
        self.deletePhase.hide()
        self.waitTime.hide()
        self.waitTimeLabel.hide()
        self.statsLabel.hide()
        self.fromStats.hide()
        self.fromStatsLabel.hide()
        self.toStats.hide()
        self.toStatsLabel.hide()
        self.addMk.setGeometry(QtCore.QRect(10, 60, 200, 31))

    def getPopUp(self, title, text):
        popup = QMessageBox()
        popup.setWindowTitle(title)
        popup.setText(text)
        popup.exec_()

    def showMainElements(self):
        self.saveMk.show()
        self.name.show()
        self.nameLabel.show()
        self.phaseEnd.show()
        self.phaseEndLabel.show()
        self.stageNumber.show()
        self.stageNumberLabel.show()
        self.light.show()
        self.lightLabel.show()
        self.tempLabel.show()
        self.maxTemp.show()
        self.maxTempLabel.show()
        self.minTemp.show()
        self.minTempLabel.show()
        self.humidityLabel.show()
        self.minHumidity.show()
        self.minHumidityLabel.show()
        self.maxHumidity.show()
        self.maxHumidityLabel.show()
        self.addPhase.show()
        self.waitTime.show()
        self.waitTimeLabel.show()
        if self.mkSelect.count() == 0:
            self.addMk.setGeometry(QtCore.QRect(10, 60, 200, 31))
        else:
            self.addMk.setGeometry(QtCore.QRect(10, 100, 200, 31))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
