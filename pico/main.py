from machine import Pin, ADC, UART, Timer
import utime
import dht
import _thread

# --- 1. CONFIGURACIÓN DE PERIFÉRICOS ---
# UART para comunicación con Pi 4 (TX=GP0, RX=GP1)
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Sensor Hall (Velocidad) - GP2
hall_pin = Pin(2, Pin.IN, Pin.PULL_UP)
pulsos = 0
velocidad = 0

# DHT11 (Temperatura) - GP15
sensor_temp = dht.DHT11(Pin(15))
temp_global = 0

# Gasolina (Potenciómetro) - GP26
adc_gas = ADC(Pin(26))

# --- 2. LÓGICA DE SENSORES ---

# Interrupción para el sensor Hall (Se activa cada vez que el imán pasa)
def contar_pulso(pin):
    global pulsos
    pulsos += 1

hall_pin.irq(trigger=Pin.IRQ_FALLING, handler=contar_pulso)

# Función para calcular velocidad (Se ejecuta cada 1 segundo)
def tick_velocidad(t):
    global pulsos, velocidad
    # Ajusta el multiplicador según el diámetro de tu rueda/maqueta
    velocidad = pulsos * 5 
    pulsos = 0

# Timer para la velocidad
tim = Timer(-1)
tim.init(period=1000, mode=Timer.PERIODIC, callback=tick_velocidad)

# Hilo dedicado al DHT11 (Lectura lenta cada 2 segundos)
def core_temperatura():
    global temp_global
    while True:
        try:
            sensor_temp.measure()
            temp_global = sensor_temp.temperature()
        except:
            # En caso de error de lectura, mantenemos el último valor
            pass
        utime.sleep(2)

# Iniciamos el hilo de temperatura
_thread.start_new_thread(core_temperatura, ())

# --- 3. BUCLE PRINCIPAL DE TRANSMISIÓN ---

print("Sistema de Telemetría Iniciado...")

while True:
    # 1. Leer Gasolina (0-100%)
    gas_pct = int((adc_gas.read_u16() / 65535) * 100)
    
    # 2. Empaquetar datos (CSV simple)
    # Formato: Velocidad, Gasolina, Temperatura
    paquete = f"{velocidad},{gas_pct},{temp_global}\n"
    
    # 3. Envío por UART hacia la Pi 4
    uart.write(paquete)
    
    # Debug por consola USB
    print(f"TX: {paquete.strip()}")
    
    # Espera corta para no saturar el buffer (20Hz de refresco)
    utime.sleep(0.01)