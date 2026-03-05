from machine import Pin, ADC, PWM
from time import sleep, ticks_ms

print("BOOT OK - Script iniciado com sucesso")

# =========================
# Configurações do projeto
# =========================

# Potenciômetro no ADC (recomendado GPIO34 no ESP32: apenas entrada)

PINO_POT = 34

# LED controlado por PWM (qualquer GPIO "normal" serve)

PINO_LED_PWM = 16
PWM_FREQ = 1000  # 1kHz (bom para LED)

# Relé (pino de controle IN do módulo)
PINO_RELE = 17

# Limiar para ligar a "lâmpada" (em % do potenciômetro)
LIGAR_EM = 70        # liga acima de 70%
DESLIGAR_EM = 65     # desliga abaixo de 65% (histerese evita trepidação)

# Suavização / transição
PASSO_SUAVIZACAO = 800   # quanto maior, mais rápido muda (0..65535)
INTERVALO_MS = 20        # loop a cada ~20ms

# =========================
# Inicialização
# =========================

pot = ADC(Pin(PINO_POT))
pot.atten(ADC.ATTN_11DB)      # faixa até ~3.3V
pot.width(ADC.WIDTH_12BIT)    # 0..4095

pwm_led = PWM(Pin(PINO_LED_PWM), freq=PWM_FREQ)
pwm_led.duty_u16(0)

rele = Pin(PINO_RELE, Pin.OUT)
rele.value(0)

# Estados
duty_atual = 0
lamp_ligada = False
ultimo_log = 0

print("=== Dimmer com Potenciometro + Rele (ESP32 / MicroPython) ===")
print("POT: GPIO", PINO_POT, "| LED PWM: GPIO", PINO_LED_PWM, "| RELE: GPIO", PINO_RELE)
print("Limiar: liga >= {}% | desliga <= {}%".format(LIGAR_EM, DESLIGAR_EM))
print("------------------------------------------------------------")

def clamp(x, a, b):
  if x < a:
    return a
  if x > b:
    return b
  return x

while True:
  # 1) Leitura do potenciômetro (0..4095)
  pot_raw = pot.read()

  # 2) Converte para 0..65535 (PWM duty_u16)
  duty_alvo = int((pot_raw * 65535) / 4095)
  duty_alvo = clamp(duty_alvo, 0, 65535)

  # 3) Transição suave (aproxima do alvo aos poucos)
  if duty_atual < duty_alvo:
    duty_atual = min(duty_atual + PASSO_SUAVIZACAO, duty_alvo)
  elif duty_atual > duty_alvo:
    duty_atual = max(duty_atual - PASSO_SUAVIZACAO, duty_alvo)

  pwm_led.duty_u16(duty_atual)

  # 4) Percentual para controle do relé
  percent = int((pot_raw * 100) / 4095)

  # 5) Relé com histerese
  if (not lamp_ligada) and (percent >= LIGAR_EM):
    lamp_ligada = True
    rele.value(1)
    print("[EVENTO] Lampada LIGADA (rele=1) - percent={}%" .format(percent))

  elif lamp_ligada and (percent <= DESLIGAR_EM):
    lamp_ligada = False
    rele.value(0)
    print("[EVENTO] Lampada DESLIGADA (rele=0) - percent={}%" .format(percent))

  # 6) Log contínuo (a cada ~300ms)
  agora = ticks_ms()
  if agora - ultimo_log >= 300:
    ultimo_log = agora
    print("pot_raw={:4d} | {:3d}% | duty_u16={:5d} | rele={}".format(
      pot_raw, percent, duty_atual, 1 if lamp_ligada else 0
    ))

  sleep(INTERVALO_MS / 1000)