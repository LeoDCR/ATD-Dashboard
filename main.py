import sys
import os
import random

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, QTimer

class Backend(QObject):
    speedChanged = Signal(float)
    rpmChanged = Signal(float)
    tempChanged = Signal(float)
    fuelChanged = Signal(float)
    lightsChanged = Signal(bool, bool)
    turnSignalsChanged = Signal(bool, bool)

    def __init__(self):
        super().__init__()
        self.simulacion_activa = True
        self.serial_port = None
        self.conectar_pico()

        self.timer = QTimer()
        self.timer.timeout.connect(self.procesar_datos)
        self.timer.start(100)
        
        self._sim_fuel = 100.0
        self._sim_tick = 0
        self._sim_speed = 0.0
        self._sim_speed_up = True

    def conectar_pico(self):
        if not SERIAL_AVAILABLE: return
        puertos = list(serial.tools.list_ports.comports())
        for p in puertos:
            if "USB" in p.description or "ACM" in p.device or "COM" in p.device:
                try:
                    self.serial_port = serial.Serial(p.device, 115200, timeout=0.1)
                    self.simulacion_activa = False
                    return
                except:
                    pass

    def procesar_datos(self):
        if self.simulacion_activa:
            self.generar_datos_simulados()
        else:
            self.leer_datos_uart()

    def generar_datos_simulados(self):
        self._sim_tick += 1
        step = 3.2 
        if self._sim_speed_up:
            self._sim_speed += step
            if self._sim_speed >= 320.0:
                self._sim_speed = 320.0
                self._sim_speed_up = False
        else:
            self._sim_speed -= step
            if self._sim_speed <= 0.0:
                self._sim_speed = 0.0
                self._sim_speed_up = True
                
        self.speedChanged.emit(self._sim_speed)
        self.rpmChanged.emit(0.0) 
        self.tempChanged.emit(85.0)
        self.fuelChanged.emit(100.0)
        self.lightsChanged.emit(False, False)
        self.turnSignalsChanged.emit(False, False)

    def leer_datos_uart(self):
        if self.serial_port and self.serial_port.in_waiting > 0:
            try:
                datos_crudos = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8')
                lineas = [l for l in datos_crudos.split('\n') if l.strip() != ""]
                
                if lineas:
                    linea = lineas[-1].strip().replace("TX:", "").strip()
                    partes = linea.split(',')
                    
                    if len(partes) >= 7:
                        velocidad = float(partes[0])
                        gasolina = float(partes[1])
                        temperatura = float(partes[2])
                        izq = (partes[3] == '1')
                        der = (partes[4] == '1')
                        baja = (partes[5] == '1')
                        alta = (partes[6] == '1')
                        
                        self.speedChanged.emit(velocidad)
                        self.rpmChanged.emit(0.0)
                        self.fuelChanged.emit(gasolina)
                        self.tempChanged.emit(temperatura)
                        self.turnSignalsChanged.emit(izq, der)
                        self.lightsChanged.emit(baja, alta)
            except Exception as e:
                pass

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    qml_path = os.path.join(os.path.dirname(__file__), "dashboard.qml")
    engine.load(qml_path)
    if not engine.rootObjects(): sys.exit(-1)
    sys.exit(app.exec())