from machine import Pin, ADC, Timer
from time import sleep

adc = ADC(Pin(26, Pin.IN))

timer = Timer()
hb = 0
def test(t):
    global hb
    hb = adc.read_u16()

timer.init(mode=Timer.PERIODIC, freq=250, callback=test)

while True:
    print(hb-33000)





