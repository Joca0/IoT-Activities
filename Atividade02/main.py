from machine import Pin, ADC
import time

# ==========================
# NOMES
# ==========================

# Pinos
PIN_SENSOR = 34      # ADC (entrada analógica)
PIN_RELE   = 25      # saída digital para relé (bomba)
PIN_LED_V  = 26      # LED Vermelho
PIN_LED_G  = 27      # LED Verde
PIN_LED_A  = 14      # LED Azul

# Limites em % (requisitos da atividade)
LIMITE_MINIMO = 30   # abaixo disso: solo seco (liga bomba)
LIMITE_MAXIMO = 70   # entre min e max: ideal

# Calibração do sensor (IMPORTANTE!)
# No Wokwi, normalmente o valor lido vai de 0 a 4095.
# Em muitos sensores: quanto MAIS úmido, MENOR a leitura.
# Ajuste estes valores conforme seu sensor / simulação.
ADC_SECO  = 3500     # leitura aproximada quando o solo está seco
ADC_UMIDO = 1200     # leitura aproximada quando o solo está bem úmido

# ==========================
# HARDWARE
# ==========================

sensor = ADC(Pin(PIN_SENSOR))
sensor.atten(ADC.ATTN_11DB)  # faixa até ~3.3V
sensor.width(ADC.WIDTH_12BIT)  # 0 a 4095

rele = Pin(PIN_RELE, Pin.OUT)
led_vermelho = Pin(PIN_LED_V, Pin.OUT)
led_verde    = Pin(PIN_LED_G, Pin.OUT)
led_azul     = Pin(PIN_LED_A, Pin.OUT)

# ==========================
# FUNÇÕES
# ==========================

def desligar_leds():
    led_vermelho.value(0)
    led_verde.value(0)
    led_azul.value(0)

def mapear_umidade_percentual(valor_adc):
    """
    Converte leitura ADC (0-4095) para % de umidade (0-100).
    Considera: SECO = valor alto, ÚMIDO = valor baixo.
    """
    # Proteção para não dar divisão por zero
    if ADC_SECO == ADC_UMIDO:
        return 0

    # Normaliza invertido: seco -> 0% | úmido -> 100%
    umidade = (ADC_SECO - valor_adc) * 100 / (ADC_SECO - ADC_UMIDO)

    # Limita entre 0 e 100
    if umidade < 0:
        umidade = 0
    if umidade > 100:
        umidade = 100

    return int(umidade)

def controlar_sistema(umidade):
    """
    Define estado (texto), liga/desliga bomba (relé) e aciona LED correto.
    """
    desligar_leds()

    if umidade < LIMITE_MINIMO:
        # Solo seco -> liga bomba + LED Vermelho
        estado = "Solo seco"
        rele.value(1)
        led_vermelho.value(1)

    elif umidade <= LIMITE_MAXIMO:
        # Umidade ideal -> bomba desligada + LED Verde
        estado = "Umidade ideal"
        rele.value(0)
        led_verde.value(1)

    else:
        # Muito úmido -> bomba desligada + LED Azul
        estado = "Solo muito úmido"
        rele.value(0)
        led_azul.value(1)

    return estado

# ==========================
# LOOP PRINCIPAL
# ==========================

print("Sistema de Irrigação Automática (ESP32 + Sensor Umidade)")
print("Iniciando...\n")

while True:
    valor_adc = sensor.read()
    umidade = mapear_umidade_percentual(valor_adc)
    estado = controlar_sistema(umidade)

    # Monitor Serial (requisito D)
    print("----- STATUS -----")
    print("Leitura ADC:", valor_adc)
    print("Umidade (%):", umidade)
    print("Estado:", estado)
    print("Bomba:", "LIGADA" if rele.value() == 1 else "DESLIGADA")
    print("------------------\n")

    time.sleep(1)