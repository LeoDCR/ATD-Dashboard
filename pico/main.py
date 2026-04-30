from machine import Pin, ADC, UART, Timer, PWM
import utime
import dht

# --- 1. CONFIGURACIÓN ---
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Sensor Hall
hall_pin = Pin(2, Pin.IN, Pin.PULL_UP)
ultimo_pulso_tiempo = 0
periodo_ms = 0
velocidad_objetivo = 0.0
velocidad_suavizada = 0.0  

# Temperatura
sensor_temp = dht.DHT11(Pin(15))
temp_global = 0
ultimo_tiempo_temp = 0

# Motores y Gasolina
adc_gas = ADC(Pin(26))
adc_acel = ADC(Pin(27))
motor_pwm = PWM(Pin(16))
motor_pwm.freq(1000)

# Switches Digitales
sw_izq = Pin(20, Pin.IN, Pin.PULL_UP)     
sw_der = Pin(21, Pin.IN, Pin.PULL_UP)     
btn_hazards = Pin(22, Pin.IN, Pin.PULL_UP) 
btn_luces = Pin(18, Pin.IN, Pin.PULL_UP)   

led_izq = Pin(10, Pin.OUT)
led_der = Pin(11, Pin.OUT)
led_baja = Pin(12, Pin.OUT)
led_alta = Pin(13, Pin.OUT)

estado_luces = 0 
btn_antes = 1
estado_hazards = False
btn_hazards_antes = 1
ultimo_debounce_hazards = 0 

ciclos_parpadeo = 0
estado_blink = False

# --- 2. INTERRUPCIÓN ---
def contar_pulso(pin):
    global ultimo_pulso_tiempo, periodo_ms
    ahora = utime.ticks_ms()
    dt = utime.ticks_diff(ahora, ultimo_pulso_tiempo)
    if dt > 5:  
        periodo_ms = dt
        ultimo_pulso_tiempo = ahora

hall_pin.irq(trigger=Pin.IRQ_FALLING, handler=contar_pulso)

# --- 3. BUCLE PRINCIPAL ---
print("Sistema listo... Mandando paquete limpio.")
utime.sleep(1)

while True:
    ahora = utime.ticks_ms()
    
    # Velocidad
    if utime.ticks_diff(ahora, ultimo_pulso_tiempo) > 500:
        periodo_ms = 0
        velocidad_objetivo = 0.0
    elif periodo_ms > 0:
        velocidad_objetivo = (1000.0 / periodo_ms) * 5.0
    velocidad_suavizada += (velocidad_objetivo - velocidad_suavizada) * 0.1

    # Temperatura
    if utime.ticks_diff(ahora, ultimo_tiempo_temp) > 2000:
        try:
            sensor_temp.measure()
            temp_global = sensor_temp.temperature()
        except:
            pass
        ultimo_tiempo_temp = ahora

    # Motor
    gas_pct = int((adc_gas.read_u16() / 65535) * 100)
    motor_pwm.duty_u16(adc_acel.read_u16())
    
    # Luces Bajas/Altas
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

    # Botón Hazards
    val_btn_h = btn_hazards.value()
    if val_btn_h == 0 and btn_hazards_antes == 1 and utime.ticks_diff(ahora, ultimo_debounce_hazards) > 250:
        estado_hazards = not estado_hazards
        ultimo_debounce_hazards = ahora
    btn_hazards_antes = val_btn_h

    # Switch Direccionales
    if estado_hazards:
        izq_activa = True
        der_activa = True
    else:
        izq_activa = (sw_izq.value() == 0)
        der_activa = (sw_der.value() == 0)
        
    ciclos_parpadeo += 1
    if ciclos_parpadeo >= 5: 
        estado_blink = not estado_blink
        ciclos_parpadeo = 0
        
    led_izq.value(1 if (izq_activa and estado_blink) else 0)
    led_der.value(1 if (der_activa and estado_blink) else 0)
    
    # --- LA LÍNEA ARREGLADA ---
    paquete = f"{velocidad_suavizada:.1f},{gas_pct},{temp_global},{int(izq_activa and estado_blink)},{int(der_activa and estado_blink)},{int(baja_on)},{int(alta_on)}\n"
    uart.write(paquete)
    print(f"TX: {paquete.strip()}")
    
    utime.sleep(0.05)