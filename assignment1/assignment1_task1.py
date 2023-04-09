from machine import Pin
from time import sleep

pin_array = [Pin(n, Pin.OUT) for n in range(20,23)]


while True:
    for i in range(4):
        for pin in pin_array:
            if i == pin_array.index(pin):
                pin.value(1)
            else:
                pin.value(0)
        sleep(1)


