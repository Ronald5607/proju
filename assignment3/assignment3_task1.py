from machine import Pin, ADC, Timer
from piotimer import Piotimer
from time import sleep
from collections import deque
import micropython
from buf import Buf

micropython.alloc_emergency_exception_buf(100)


        


class heartbeater:

    MAX_SAMPLES = 1000
    ITERATIONS = 3
    NOISE_CONTROL = 2
    FREQ = 250
    AVERAGE_SIZE = 10

    def __init__(self) -> None:
        self._adc = ADC(Pin(27))
        
        # self.samples = deque((), heartbeater.MAX_SAMPLES)
        self.samples = Buf(size=1000)
        self._adc_timer = Piotimer(mode=Timer.PERIODIC, freq=heartbeater.FREQ, callback=self._add_samples)
        self.min_sample = 0
        self.bpm = 0
        self._calculating = False
        self._count = 0
        self._divisor = 0
        self._divided = 0

    def _get_average(self, samples):
        return sum(samples)//len(samples)

    def print_samples_to_file(self):
        with open('jep.txt', 'w') as filu:
            for i in range(len(self.samples)-1):
                filu.write(str(self.samples[i]))
                filu.write('\n')

        with open('jep2.txt', 'w') as filu:
            while len(self.samples) > 10:
                if self._find_rising_edge():
                    filu.write(str(self.samples.count))
                    filu.write('\n')

        
    def _read(self) -> int:
        return self._adc.read_u16()
    
    def _pop(self):
        self._count += 1
        return self.samples.get()
    
    def _add_samples(self, timer) -> None:
        if not self._calculating:
            self.samples.put(self._read())

    def _average_gradient(self, samples) -> float:
        div = 0
        length = len(samples) - 1
        for i in range(length):
            div += samples[i+1]/samples[i]
        return div/length


    def _find_rising_edge(self) -> bool:
        if len(self.samples) <= 10:
            raise Exception('sample pool too low.')
        buffer = self.samples[0:10]
        while len(self.samples) > 10:
            avg_gradient = self._average_gradient(buffer)
            print(avg_gradient)
            if avg_gradient > 1:
                return True
            else:
                buffer.append(self.samples.get())
        return False
                

    
    def _time_between_peaks(self) -> float:
        if self._find_rising_edge():
            self._count = 0
            while True:
                if len(self.samples) < heartbeater.ITERATIONS:
                    return 0
                if self._find_rising_edge():
                    time = self._count * 1/heartbeater.FREQ
                    if time > 0.1:
                        print(self._count, time)
                        return time
        return 0

    def calculate_bpm(self) -> int:
        self._calculating = True
        time = self._time_between_peaks()
        if time:
            self._divided += time
            self._divisor += 1
            self.bpm = round(60/(self._divided/self._divisor))
        self._calculating = False
        return self.bpm



hb = heartbeater()
while len(hb.samples) < 999:
    sleep(0.1)
hb._adc_timer.deinit()
print('done populating samples')

hb.print_samples_to_file()
print('done')



# while True:
    # sleep(0.3)
    # print(hb._find_rising_edge())
    # print(hb.calculate_bpm())
    # if len(hb.samples) > 998:
    #     hb.print_samples()

