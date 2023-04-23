from machine import Pin, PWM, Timer, I2C
import ssd1306
import framebuf
from time import sleep, ticks_add, ticks_diff, ticks_ms

class led:
    def __init__(self, n) -> None:
        self.pwm = PWM(Pin(n, Pin.OUT))
        self.pwm.freq(500)
        self.pwm.duty_u16(0)
        self.brightness = 0
    
    def set_brightness(self, number):
        if number > 100:
            number = 100
        elif number < 0:
            number = 0
        self.pwm.duty_u16(10 * number)
        self.brightness = number


led_array = [led(n) for n in range(20, 23)]

prev_time = ticks_ms()


class Drawer:
    def __init__(self) -> None:
        self.blinkmode = False
        self.time = ticks_ms()
        self.prev_time = self.time
        self.fps = self.time
        self.selector_fbuf = framebuf.FrameBuffer(bytearray((2 * (9+2*18)) * 2), 2, 45, framebuf.MONO_HLSB)
        self.brightfbufbuf = [framebuf.FrameBuffer(bytearray(1624), 100, 7, framebuf.MONO_HLSB) for i in range(3)]
        self.textbufbuf = [framebuf.FrameBuffer(bytearray(3*8*8*2), 3*8, 8, framebuf.MONO_HLSB) for i in range(3)]
        i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
        self.display = ssd1306.SSD1306_I2C(128, 64, i2c)
        self.mode = True
        self.rot = 0
        self.rotary_button = Pin(12, Pin.IN, Pin.PULL_UP)
        self.rot_a = Pin(10, Pin.IN)
        self.rot_b = Pin(11, Pin.IN)
        self.rot_a.irq(trigger=Pin.IRQ_RISING, handler=self.hand)
        self.rotary_button.irq(trigger=Pin.IRQ_RISING, handler=self.btnhand)

    def hand(self, p):
        self.rot += -1 if self.rot_b.value() else 1

    def btnhand(self, p):
        tick_time = ticks_ms()
        if ticks_diff(tick_time, self.prev_time) > 20:
            self.mode = False if self.mode else True
            self.prev_time = tick_time

    def draw_once(self):
        self.display.fill(0)
        for i in range(3):
            if i == 0:
                text = 'LED ONE'
            elif i == 1:
                text = 'LED TWO'
            else:
                text = 'LED THREE'
            self.display.text(text, 5, 1+i*18, 1)
            self.display.rect(5, 9+i*18, 102, 9, 1)

        self.draw_brightness_text()
        self.display.show()

    def blink(self):
        time = ticks_ms()
        if ticks_diff(time, self.time) > 500:
            self.blinkmode = False if self.blinkmode else True
            self.time = time

    def draw_selector(self, index, blinking):
        self.selector_fbuf.fill(0)
        if blinking and self.blinkmode:
            pass
        else:
            self.selector_fbuf.fill_rect(0, index*18, 2, 9, 1)
        self.display.blit(self.selector_fbuf, 0, 9)

    def draw_brightness_text(self, index=4):
        for i in range(3):
            self.textbufbuf[i].fill(0)
            if i == index and self.blinkmode:
                pass
            else:
                if led_array[i].brightness < 10:
                    text = '  '+str(led_array[i].brightness)
                elif led_array[i].brightness == 100:
                    text = str(led_array[i].brightness)
                else:
                    text = ' '+str(led_array[i].brightness)
                self.textbufbuf[i].text(text, 0, 0, 1)
            self.display.blit(self.textbufbuf[i], 84, 1+i*18)

    def draw_brightness(self):
        for i in range(3):
            self.brightfbufbuf[i].fill(0)
            self.brightfbufbuf[i].fill_rect(0, 0, led_array[i].brightness, 7, 1)
            self.display.blit(self.brightfbufbuf[i], 6, 10+i*18)

    def show(self):
        new_fps = ticks_ms()
        if ticks_diff(new_fps, self.fps) > 66:
            self.display.show()
            self.fps = new_fps


drawer = Drawer()
set = False
recently_changed = False
index = 0
fps = ticks_ms()
drawer.draw_once()
while True:
    if drawer.mode:
        if set:
            drawer.rot = index
            drawer.draw_brightness_text()
            set = False
        index = drawer.rot % 3
        drawer.draw_selector(index, True)
    else:
        if not set:
            drawer.rot = led_array[index].brightness
            drawer.draw_selector(index, False)
            set = True
        led_array[index].set_brightness(drawer.rot)
        drawer.draw_brightness_text(index=index)
        drawer.draw_brightness()
    drawer.blink()
    fps2 = ticks_ms()
    drawer.show()
