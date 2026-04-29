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

    # --- "Megáfonos" hacia la pantalla QML ---

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

        

        # --- VARIABLES DE LA NUEVA SIMULACIÓN ---

        self._sim_fuel = 100.0

        self._sim_tick = 0

        self._sim_speed = 0.0       # Empezamos en 0

        self._sim_speed_up = True   # Controla si va subiendo o bajando



    def conectar_pico(self):

        if not SERIAL_AVAILABLE:

            return

        puertos = list(serial.tools.list_ports.comports())

        for p in puertos:

            if "USB" in p.description or "ACM" in p.device or "COM" in p.device:

                try:

                    self.serial_port = serial.Serial(p.device, 115200, timeout=0.1)

                    self.simulacion_activa = False

                    print(f"✅ Conectado a la Pico en: {p.device}")

                    return

                except Exception as e:

                    print(f"❌ Error al conectar en {p.device}: {e}")

        if self.simulacion_activa:

            print("⚠️ Pico no detectada. Iniciando MODO BARRIDO (Sweep Test).")



    def procesar_datos(self):

        if self.simulacion_activa:

            self.generar_datos_simulados()

        else:

            self.leer_datos_uart()



    def generar_datos_simulados(self):

        self._sim_tick += 1

        

        # --- LA MAGIA DEL BARRIDO 0 a 320 ---

        step = 3.2 # Sube 3.2 km/h cada 100ms (tarda 10 segundos en llegar a 320)

        

        if self._sim_speed_up:

            self._sim_speed += step

            if self._sim_speed >= 320.0:

                self._sim_speed = 320.0

                self._sim_speed_up = False # Llegó al tope, ahora baja

        else:

            self._sim_speed -= step

            if self._sim_speed <= 0.0:

                self._sim_speed = 0.0

                self._sim_speed_up = True  # Llegó a cero, ahora sube

                

        # Variables random para que no se vea muerto lo demás

        temp = 85.0 + random.uniform(-2, 2)

        self._sim_fuel -= 0.1

        if self._sim_fuel <= 0: self._sim_fuel = 100

        

        left = True if (self._sim_tick % 20 < 10) else False

        right = not left

        low = True

        high = True if (self._sim_tick % 100 < 50) else False



        # Emitimos la velocidad del barrido en lugar del random

        self.speedChanged.emit(self._sim_speed)

        self.rpmChanged.emit(0.0) 

        self.tempChanged.emit(temp)

        self.fuelChanged.emit(self._sim_fuel)

        self.lightsChanged.emit(low, high)

        self.turnSignalsChanged.emit(left, right)



    def leer_datos_uart(self):

        if self.serial_port and self.serial_port.in_waiting > 0:

            try:

                datos_crudos = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8')

                lineas = datos_crudos.split('\n')

                

                lineas_validas = [l for l in lineas if l.strip() != ""]

                

                if lineas_validas:

                    linea = lineas_validas[-1].strip()

                    

                    if "TX:" in linea:

                        linea = linea.replace("TX:", "").strip()

                        

                    partes = linea.split(',')

                    if len(partes) >= 3:

                        velocidad = float(partes[0])

                        gasolina = float(partes[1])

                        temperatura = float(partes[2])

                        

                        self.speedChanged.emit(velocidad)

                        self.rpmChanged.emit(0.0)

                        self.fuelChanged.emit(gasolina)

                        self.tempChanged.emit(temperatura)

                        self.turnSignalsChanged.emit(False, False)

                        self.lightsChanged.emit(True, False)

            except Exception as e:

                pass



if __name__ == "__main__":

    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    

    backend = Backend()

    engine.rootContext().setContextProperty("backend", backend)

    

    qml_path = os.path.join(os.path.dirname(__file__), "dashboard.qml")

    engine.load(qml_path)

    

    if not engine.rootObjects(): 

        sys.exit(-1)

    

    sys.exit(app.exec())