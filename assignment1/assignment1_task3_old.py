from machine import Pin
from time import sleep
import math

def pulse_led(pin, frequency, duty):
    on_time = (1/frequency) * (duty/100)
    off_time = (1/frequency) * (1-duty/100)
    pin.value(1)
    sleep(on_time)
    pin.value(0)
    sleep(off_time)


def smooth_led(pin, value):
    t1 = 0
    t2 = 50
    freq = 150
    if value:
        for x in range(t1, t2):
            pulse_led(pin, freq, x)
            # sleep((math.sin(math.pi*(x/t2))/(t2)))
    else:
        for x in reversed(range(t1, t2)):
            pulse_led(pin, freq, x)
        pin.value(0)

x = 0b000
pin_value = [0, 0, 0]
pin_change = [0, 0, 0]

pin_array = [Pin(n, Pin.OUT) for n in range(20,23)]

freq = 100
while True:
    for pin in pin_array:
        i = pin_array.index(pin)
        # (x & (1 << i)) >> i
        print(pin_value[i], ((x & (1 << i)) >> i))
        if pin_value[i] != ((x & (1 << i)) >> i):
            pin_change[i] = 1
            pin_value[i] = (x & (1 << i)) >> i
        else:
            pin_change[i] = 0
    print(pin_value)
    for pin in pin_array:
        i = pin_array.index(pin)
        if pin_change[i]:
                if pin_value[i]:
                    for y in range(100):
                        pulse_led(pin, freq, y)
                else:
                    for y in reversed(range(100)):
                        pulse_led(pin, freq, y)
        else:
            pin.value(pin_value[i])

    sleep(1)
    x += 1

        