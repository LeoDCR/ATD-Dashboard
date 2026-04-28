from machine import Pin, ADC, UART, Timer, PWM

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



# Gasolina (Potenciómetro original) - GP26

adc_gas = ADC(Pin(26))



# --- NUEVO: SIMULADOR DE MOTOR ---

# Potenciómetro del acelerador - GP27

adc_acelerador = ADC(Pin(27))

# Motor controlado por PWM - GP16

motor_pwm = PWM(Pin(16))

motor_pwm.freq(1000) # Frecuencia de 1kHz



# --- 2. LÓGICA DE SENSORES ---

def contar_pulso(pin):

    global pulsos

    pulsos += 1



hall_pin.irq(trigger=Pin.IRQ_FALLING, handler=contar_pulso)



def tick_velocidad(t):

    global pulsos, velocidad

    # Aquí puedes cambiar el 5 por el multiplicador real de tu llanta luego

    velocidad = pulsos * 5 

    pulsos = 0



tim = Timer(-1)

tim.init(period=1000, mode=Timer.PERIODIC, callback=tick_velocidad)



def core_temperatura():

    global temp_global

    while True:

        try:

            sensor_temp.measure()

            temp_global = sensor_temp.temperature()

        except:

            pass

        utime.sleep(2)



_thread.start_new_thread(core_temperatura, ())



# --- 3. BUCLE PRINCIPAL DE TRANSMISIÓN ---

print("Sistema de Telemetría y Simulador Iniciados...")



while True:

    # 1. Leer Gasolina (0-100%)

    gas_pct = int((adc_gas.read_u16() / 65535) * 100)

    

    # --- 2. NUEVO: Leer acelerador y mover motor ---

    lectura_acel = adc_acelerador.read_u16() # Lee de 0 a 65535

    motor_pwm.duty_u16(lectura_acel)         # Manda la fuerza al motor

    

    # 3. Empaquetar datos (Velocidad, Gasolina, Temperatura)

    paquete = f"{velocidad},{gas_pct},{temp_global}\n"

    

    # 4. Envío por UART hacia la Pi 4

    uart.write(paquete)

    

    # Debug por consola (opcional, para que veas qué manda)

    print(f"TX: {paquete.strip()}")

    

    # Espera exacta para no saturar la Raspberry (Cero Delay)

    utime.sleep(0.1)