from machine import Pin, PWM
from time import sleep

pin_array = [Pin(n, Pin.OUT) for n in range(20,23)]

pwm_array = [PWM(pin) for pin in pin_array]
for pwm in pwm_array:
    pwm.freq(500)
    pwm.duty_u16(0)

x = 0b000

while True:
    for pin in pin_array:
        i = pin_array.index(pin)
        if ((x & (1 << i)) >> i) and pwm_array[i].duty_u16() == 0:
            for n in range(500):
                pwm_array[i].duty_u16(n)
                sleep(0.001)
        elif not ((x & (1 << i)) >> i) and pwm_array[i].duty_u16() > 0:
            for n in reversed(range(500)):
                pwm_array[i].duty_u16(n)
                sleep(0.001)
    sleep(1)
    x += 1
    if x > 0b111:
        x = 0