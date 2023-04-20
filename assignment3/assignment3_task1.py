from machine import Pin, ADC, Timer
from piotimer import Piotimer
from time import sleep
import micropython
from buf import Buf

micropython.alloc_emergency_exception_buf(100)


class heartbeater:

    FREQ = 250
    AVERAGE_SIZE = 20
    BUF_SIZE = 40
    FRE = 20


    def __init__(self) -> None:
        self._adc = ADC(Pin(27))
        
        # self.samples = deque((), heartbeater.MAX_SAMPLES)
        self.samples = Buf(size=heartbeater.BUF_SIZE)
        self._adc_timer = Piotimer(mode=Timer.PERIODIC, freq=heartbeater.FREQ, callback=self._add_samples)
        self.running = False
        self.tmp_data= []
        self.average_buf = Buf(size=heartbeater.AVERAGE_SIZE)
        self.avg = 0
        self.ca = 0
        self.ca_count = 0


    def _get_threshold(self, sample):
        self.ca_count += 1
        self.ca += (sample - self.ca) // (self.ca_count)
        return self.ca


    def print_samples_to_file(self, number_of_samples: int, style) -> None:
        filu1 = open('jep.txt', 'w')
        filu2 = open('jep2.txt', 'w')
        last_count = 0
        cumulative_count = -heartbeater.FRE if style=='fre' else -1
        while len(self.tmp_data) < number_of_samples:
            if style == 'fre':
                count = self._find_rising_edge(printing=True)
            else:
                count = self._find_peak(printing=True)
            cumulative_count += count
            delta = cumulative_count - last_count
            if self._validate(delta):
                last_count = cumulative_count
                filu2.write(str(cumulative_count))
                filu2.write('\n')
            else:
                if delta > 380:
                    last_count = cumulative_count
                    filu2.write(str(-cumulative_count))
                    filu2.write('\n')
                else:
                    filu2.write(str(-cumulative_count))
                    filu2.write('\n')
        for data in self.tmp_data:
            filu1.write(str(data))
            filu1.write('\n')

        filu1.close()
        filu2.close()
            

        
    def _read(self) -> int:
        return self._adc.read_u16()


    def _pop(self) -> int:
        return self.samples.get()


    def _add_samples(self, timer) -> None:
        self.samples.put(self._read())


    def _running_average(self, sample) -> int:
        self.average_buf.append(sample)
        if not self.avg:
            self.avg = sample
            return self.avg
        self.avg += (sample - self.average_buf[0])//len(self.average_buf)
        return self.avg
        

    def _printing(self, sample):
        self.tmp_data.append(sample)

    def _find_peak(self, printing=False):
        if self.samples.empty():
            self._wait_for_samples(1)
        first_sample = self._running_average(self._pop())
        self._get_threshold(first_sample)
        if printing:
            self._printing(first_sample)
        while True:
            if self.samples.empty():
                continue
            second_sample = self._running_average(self._pop())
            threshold = self._get_threshold(second_sample) * 1.1
            if printing:
                self._printing(second_sample)
            if (first_sample > second_sample) and (first_sample > threshold):
                count = self.samples.count
                self.samples.count = 0
                return count
            first_sample = second_sample

    
    def _find_rising_edge(self, printing=False) -> int:
        i = 0
        error = False
        threshold = 33000
        if self.samples.empty():
            self._wait_for_samples(1)
        first_sample = self._running_average(self._pop())
        if printing:
            self._printing(first_sample)
        while True:
            if self.samples.empty():
                continue
            second_sample = self._running_average(self._pop())
            if printing:
                self._printing(second_sample)
            if second_sample - first_sample > 100:
                i += 1
            elif error:
                error = False
                i = 0
            else:
                error = True
            if i >= heartbeater.FRE and second_sample > threshold:
                count = self.samples.count
                self.samples.count = 0
                return count
            first_sample = second_sample


    def calculate_bpm(self, delta):
        return (heartbeater.FREQ * 60) / delta
    
    def _validate(self, count):
        if 115 < count < 380:
            return True
        return False
    
    def _wait_for_samples(self, n) -> None:
        while len(self.samples) <= n:
                continue

    def run(self, style):
        self.running = True
        if style == 'fre':
            cumulative_count = -heartbeater.FRE
        else:
            cumulative_count = -1
        while self.running:
            if style == 'fre':
                count = self._find_rising_edge()
            else:
                count = self._find_peak()
            cumulative_count += count
            if self._validate(cumulative_count):
                print(self.calculate_bpm(cumulative_count))
                cumulative_count = 0
            elif cumulative_count > 380:
                cumulative_count = 0


hb = heartbeater()

# hb.print_samples_to_file(2000, style='aa')
hb.run(style='fp')


