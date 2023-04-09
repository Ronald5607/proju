from machine import Pin
from time import sleep

x = 0b000

pin_array = [Pin(n, Pin.OUT) for n in range(20,23)]

while True:
    for pin in pin_array:
        i = pin_array.index(pin)
        pin.value((x & (1 << i)) >> i)
    sleep(1)
    x += 1
    if x > 0b111:
        x = 0

        