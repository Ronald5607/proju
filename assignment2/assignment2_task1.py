from machine import Pin, PWM, I2C
from time import sleep
import ssd1306

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

display = ssd1306.SSD1306_I2C(128, 64, i2c)

pwm_array = [PWM(Pin(n, Pin.OUT)) for n in range(20, 23)]
for pwm in pwm_array:
    pwm.freq(500)
    pwm.duty_u16(0)

button_array = [Pin(n, Pin.IN, Pin.PULL_UP) for n in range(7,10)]
rotary_button = Pin(12, Pin.IN, Pin.PULL_UP)

def interrupt_handler(pin):
    for pwm in pwm_array:
        pwm.duty_u16(0)

rotary_button.irq(handler=interrupt_handler, trigger=Pin.IRQ_FALLING)

recenty_pressed = [False, False, False]
while True:
    for button in button_array:
        i = button_array.index(button)

        if not button.value() and not recenty_pressed[i]:
            recenty_pressed[i] = True
            pwm = pwm_array[i]
            pwm.duty_u16(0) if pwm.duty_u16() else pwm.duty_u16(500)
        elif button.value() and recenty_pressed[i]:
            recenty_pressed[i] = False

    display.fill(0) 
    for pwm in pwm_array:
        duty = pwm.duty_u16()
        i = pwm_array.index(pwm)
        display.text(f'LED {i}: {"ON" if duty else "OFF"}', 0, i*10)
    display.show()
    