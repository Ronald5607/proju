from machine import Pin

pin_array = [Pin(n, Pin.OUT) for n in range(20,23)]

for pin in pin_array:
    pin.value(0)