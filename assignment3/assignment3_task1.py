from machine import Pin, ADC, Timer
from piotimer import Piotimer
from time import sleep
import micropython
from buf import Buf

micropython.alloc_emergency_exception_buf(100)


class heartbeater:

    MAX_SAMPLES = 1000
    ITERATIONS = 3
    NOISE_CONTROL = 2
    FREQ = 250
    AVERAGE_SIZE = 10
    BUF_SIZE = 30


    def __init__(self) -> None:
        self._adc = ADC(Pin(27))
        
        # self.samples = deque((), heartbeater.MAX_SAMPLES)
        self.samples = Buf(size=1000)
        self._adc_timer = Piotimer(mode=Timer.PERIODIC, freq=heartbeater.FREQ, callback=self._add_samples)
        self._calculating = False
        self._count = 0


    def _get_average(self, samples):
        return sum(samples)//len(samples)


    def print_samples_to_file(self, samples) -> None:
        with open('jep.txt', 'w') as filu:
            for i in range(len(samples)-1):
                filu.write(str(samples[i]))
                filu.write('\n')

        with open('jep2.txt', 'w') as filu:
            while len(samples) > heartbeater.BUF_SIZE:
                if self._find_rising_edge(samples):
                    filu.write(str(samples.count-heartbeater.BUF_SIZE))
                    filu.write('\n')

        
    def _read(self) -> int:
        return self._adc.read_u16()


    def _pop(self) -> int:
        self._count += 1
        return self.samples.get()


    def _add_samples(self, timer) -> None:
        if not self._calculating:
            self.samples.put(self._read())


    def _running_average(self, samples: Buf):
        new_samples = Buf(size=len(samples))
        new_samples.put(samples[0])
        for i in range(1, len(samples) - 1):
            new_samples.put((samples[i-1]+samples[i]+samples[i+1])//3) # type: ignore
        new_samples.put(samples[len(samples)-1])
        return new_samples


    def _average_gradient(self, samples: Buf) -> float:
        div = 0
        length = len(samples) - 1
        for i in range(length):
            div += samples[i+1] - samples[i] # type: ignore
        return div/length


    def _find_rising_edge(self, samples) -> bool:
        if len(samples) <= heartbeater.BUF_SIZE:
            return False
        buffer = samples[0:heartbeater.BUF_SIZE]
        while len(samples) > heartbeater.BUF_SIZE:
            avg_gradient = self._average_gradient(buffer)
            if avg_gradient > 100:
                return True
            else:
                buffer.append(samples.get())
        return False
    

hb = heartbeater()
while len(hb.samples) < 1000:
    sleep(0.1)
hb._adc_timer.deinit()
print('done populating samples')

samples = hb._running_average(hb.samples)
hb.print_samples_to_file(samples)
print('done')



# while True:
    # sleep(0.3)
    # print(hb._find_rising_edge())
    # print(hb.calculate_bpm())
    # if len(hb.samples) > 998:
    #     hb.print_samples()

