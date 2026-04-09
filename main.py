import sys
import os
import random

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠️ pyserial no instalado. Corre: pip install pyserial")

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
        
        # 1. Busca si hay una Pico real conectada
        self.conectar_pico()

        # 2. Arranca el reloj (cada 100ms pide datos)
        self.timer = QTimer()
        self.timer.timeout.connect(self.procesar_datos)
        self.timer.start(100)
        
        self._sim_fuel = 100.0
        self._sim_tick = 0

    def conectar_pico(self):
        if not SERIAL_AVAILABLE:
            return

        puertos = list(serial.tools.list_ports.comports())
        for p in puertos:
            # Busca un puerto USB en Windows (COM) o Linux (ttyACM/ttyUSB)
            if "USB" in p.description or "ACM" in p.device or "COM" in p.device:
                try:
                    self.serial_port = serial.Serial(p.device, 115200, timeout=0.1)
                    self.simulacion_activa = False
                    print(f"✅ Conectado a la Pico real en: {p.device}")
                    return
                except Exception as e:
                    print(f"❌ Error al conectar en {p.device}: {e}")
        
        if self.simulacion_activa:
            print("⚠️ No se encontró la Pico. Iniciando en MODO SIMULACIÓN (Random).")

    def procesar_datos(self):
        # Decide de dónde saca la información
        if self.simulacion_activa:
            self.generar_datos_simulados()
        else:
            self.leer_datos_uart()

    def generar_datos_simulados(self):
        """Genera números temblorosos para que el diseñador trabaje a gusto en Windows"""
        self._sim_tick += 1
        speed = random.uniform(40, 45)
        rpm = random.uniform(4000, 4200)
        temp = 85.0 + random.uniform(-2, 2)
        
        self._sim_fuel -= 0.1
        if self._sim_fuel <= 0: self._sim_fuel = 100
        
        left = True if (self._sim_tick % 20 < 10) else False
        right = not left
        low = True
        high = True if (self._sim_tick % 100 < 50) else False

        self.speedChanged.emit(speed)
        self.rpmChanged.emit(rpm)
        self.tempChanged.emit(temp)
        self.fuelChanged.emit(self._sim_fuel)
        self.lightsChanged.emit(low, high)
        self.turnSignalsChanged.emit(left, right)

    def leer_datos_uart(self):
        """Despedaza el texto real que llega desde el USB de la Pico"""
        if self.serial_port and self.serial_port.in_waiting > 0:
            try:
                linea = self.serial_port.readline().decode('utf-8').strip()
                
                partes = linea.split(',')
                datos = {}
                for parte in partes:
                    if ':' in parte:
                        letra, numero = parte.split(':')
                        datos[letra] = float(numero)
                
                if 'V' in datos: self.speedChanged.emit(datos['V'])
                if 'R' in datos: self.rpmChanged.emit(datos['R'])
                if 'T' in datos: self.tempChanged.emit(datos['T'])
                if 'F' in datos: self.fuelChanged.emit(datos['F'])
                
                if 'L' in datos:
                    estado_luz = int(datos['L'])
                    self.lightsChanged.emit((estado_luz == 1 or estado_luz == 2), (estado_luz == 2))
                
                if 'I' in datos:
                    estado_int = int(datos['I'])
                    self.turnSignalsChanged.emit((estado_int == 1), (estado_int == 2))
                    
            except Exception as e:
                # Si llega basura un milisegundo, la ignora y no crashea
                pass

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    
    engine.load(os.path.join(os.path.dirname(__file__), "dashboard.qml"))
    
    if not engine.rootObjects(): 
        sys.exit(-1)
    
    sys.exit(app.exec())