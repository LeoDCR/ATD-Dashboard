from machine import Pin, ADC, UART, Timer, PWM
import utime
import dht

# --- 1. CONFIGURACIÓN ---
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Sensores Anteriores
hall_pin = Pin(2, Pin.IN, Pin.PULL_UP)
pulsos = 0
velocidad = 0
ultimo_pulso_tiempo = 0
historial_vel = [0, 0, 0, 0, 0]

sensor_temp = dht.DHT11(Pin(15))
temp_global = 0
ultimo_tiempo_temp = 0 # <- NUEVO: Control de tiempo sin hilos

adc_gas = ADC(Pin(26))
adc_acel = ADC(Pin(27))
motor_pwm = PWM(Pin(16))
motor_pwm.freq(1000)

# Luces y Direccionales
adc_direccionales = ADC(Pin(28)) 
btn_luces = Pin(18, Pin.IN, Pin.PULL_UP) 

led_izq = Pin(10, Pin.OUT)
led_der = Pin(11, Pin.OUT)
led_baja = Pin(12, Pin.OUT)
led_alta = Pin(13, Pin.OUT)

estado_luces = 0 
btn_antes = 1
ciclos_parpadeo = 0
estado_blink = False

# --- 2. INTERRUPCIONES Y TIMERS ---
def contar_pulso(pin):
    global pulsos, ultimo_pulso_tiempo
    ahora = utime.ticks_ms()
    if utime.ticks_diff(ahora, ultimo_pulso_tiempo) > 50:
        pulsos += 1
        ultimo_pulso_tiempo = ahora

hall_pin.irq(trigger=Pin.IRQ_FALLING, handler=contar_pulso)

def tick_velocidad(t):
    global pulsos, velocidad, historial_vel
    vel_bruta = pulsos * 5 
    pulsos = 0
    historial_vel.pop(0)
    historial_vel.append(vel_bruta)
    velocidad = sum(historial_vel) / len(historial_vel)

tim = Timer(-1)
tim.init(period=1000, mode=Timer.PERIODIC, callback=tick_velocidad)

# --- 3. BUCLE PRINCIPAL ---
print("Sistema listo... Arrancando en 3, 2, 1...")
utime.sleep(1)

while True:
    ahora = utime.ticks_ms()
    
    # 1. Leer Temperatura cada 2 segundos sin trabar la Pico
    if utime.ticks_diff(ahora, ultimo_tiempo_temp) > 2000:
        try:
            sensor_temp.measure()
            temp_global = sensor_temp.temperature()
        except:
            pass
        ultimo_tiempo_temp = ahora

    # 2. Gasolina y Motor
    gas_pct = int((adc_gas.read_u16() / 65535) * 100)
    lectura_acel = adc_acel.read_u16() 
    motor_pwm.duty_u16(lectura_acel)
    
    # 3. Lógica del Botón de Luces
    btn_ahora = btn_luces.value()
    if btn_ahora == 0 and btn_antes == 1:
        estado_luces += 1
        if estado_luces > 2:
            estado_luces = 0
    btn_antes = btn_ahora
    
    baja_on = (estado_luces == 1 or estado_luces == 2)
    alta_on = (estado_luces == 2)
    
    led_baja.value(baja_on)
    led_alta.value(alta_on)

    # 4. Lógica de Direccionales
    val_dir = adc_direccionales.read_u16()
    izq_activa = False
    der_activa = False
    
    if val_dir < 28000:       
        izq_activa = True
    elif val_dir > 38000:     
        der_activa = True
        
    # 5. Generador de Parpadeo
    ciclos_parpadeo += 1
    if ciclos_parpadeo >= 5: 
        estado_blink = not estado_blink
        ciclos_parpadeo = 0
        
    led_izq.value(1 if (izq_activa and estado_blink) else 0)
    led_der.value(1 if (der_activa and estado_blink) else 0)
    
    # 6. Mandar paquete
    paquete = f"{velocidad:.1f},{gas_pct},{temp_global},{int(izq_activa and estado_blink)},{int(der_activa and estado_blink)},{int(baja_on)},{int(alta_on)}\n"
    uart.write(paquete)
    
    # ¡AQUÍ ESTÁ LA LÍNEA MÁGICA DE REGRESO!
    print(f"TX: {paquete.strip()}")
    
    utime.sleep(0.1)