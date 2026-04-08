import sys
import os
import struct
import smbus2
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, QTimer

# --- CONFIGURACIÓN I2C ---
I2C_ADDRESS = 0x08
I2C_BUS = 1

class Backend(QObject):
    speedChanged = Signal(float)
    rpmChanged = Signal(float)
    tempChanged = Signal(float)
    battChanged = Signal(float)

    def __init__(self):
        super().__init__()
        self._speed = 0.0
        self._rpm = 0.0
        self._temp = 0.0
        self._batt = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_sensors)
        self.timer.start(100)

    def read_sensors(self):
        try:
            with smbus2.SMBus(I2C_BUS) as bus:
                data = bus.read_i2c_block_data(I2C_ADDRESS, 0, 16)
                valores = struct.unpack('ffff', bytearray(data))
                self._speed = round(valores[0], 1)
                self._rpm = round(valores[1], 0)
                self._temp = round(valores[2], 1)
                self._batt = round(valores[3], 1)
                self.speedChanged.emit(self._speed)
                self.rpmChanged.emit(self._rpm)
                self.tempChanged.emit(self._temp)
                self.battChanged.emit(self._batt)
                print(f"Datos: {self._speed}, {self._rpm}, {self._temp}, {self._batt}")
        except Exception as e:
            print(f"Esperando Arduino... ({e})")

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(os.path.join(os.path.dirname(__file__), "dashboard.qml"))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())