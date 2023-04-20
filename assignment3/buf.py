from fifo import Fifo
import array


class Buf:
    def __init__(self, *iter, size=None):
        self.data = array.array('H')
        if size:
            for i in range(size):
                self.data.append(0)
            self.size = size
            self.head = 0
            self._empty = True
        else:
            for iterables in iter:
                for element in iterables:
                    self.data.append(element)
            self.size = sum(len(i) for i in iter) # type: ignore
            self.head = self.size - 1
            if self.head != 0:
                self._empty = False
            else:
                self._empty = True
        self.tail = 0
        self.dc = 0
        self.count = 0

    def empty(self):
        return self._empty
    
    def put(self, value):
        nh = (self.head + 1) % self.size
        if (nh-1)%self.size == self.tail and not self.empty():
            self.dc = self.dc + 1
        else:
            self._empty = False
            self.data[self.head] = value
            self.head = nh

    def get(self):
        if not self.empty():
            val = self.data[self.tail]
            self.count += 1
            self.tail = (self.tail + 1) % self.size
            if self.tail == self.head and not self.empty():
                self._empty = True
            return val
        raise ValueError('Empty buffer.')
    
    def append(self, value):
        new_head = (self.head + 1) % self.size
        if (new_head-1)%self.size == self.tail and not self.empty():
            self.tail = (self.tail + 1) % self.size
        self._empty = False
        self.data[self.head] = value
        self.head = new_head

    def get_real_index(self, index) -> int:
        is_over, true_index = divmod(self.tail + index, self.size)
        if is_over > 1:
            raise IndexError(f'Out of bounds. Tail: {self.tail}, Head: {self.head}, True index: {true_index}, Is_over: {is_over}')
        if self.tail < self.head:
            if (true_index > self.head) or is_over:
                raise IndexError(f'Out of bounds. Tail: {self.tail}, Head: {self.head}, True index: {true_index}, Is_over: {is_over}')
        elif self.tail > self.head:
            if is_over:
                if true_index > self.head:
                    raise IndexError(f'Out of bounds. Tail: {self.tail}, Head: {self.head}, True index: {true_index}, Is_over: {is_over}')
            else:
                if true_index < self.head:
                    raise IndexError(f'Out of bounds. Tail: {self.tail}, Head: {self.head}, True index: {true_index}, Is_over: {is_over}')
        return true_index
    

    def __getitem__(self, index):
        if isinstance(index, int):
            if index < 0:
                true_index = self.get_real_index(self.head + index)
            true_index = self.get_real_index(index)
            return self.data[true_index]

        elif isinstance(index, slice):
            if (index.start < 0) or (index.stop < 0):
                raise IndexError('No support for negative indices.')
            if index.start == index.stop:
                raise Exception('what')
            start = self.get_real_index(index.start)
            stop = self.get_real_index(index.stop)
            if (index.start < index.stop) and not index.start:
                length = stop - start
                self.tail += length
                self.count += length
            if start > stop:
                return Buf(self.data[start:self.size-1]+self.data[0:stop])
            return Buf(self.data[start:stop])
        raise TypeError('Only ints and slices supported.')
    
    def __setitem__(self, index, value) -> None:
        if not isinstance(index, int):
            raise TypeError('Key can only be an int.')
        true_index = self.get_real_index(index)
        self.data[true_index] = value
        
    def __len__(self):
        if self.empty():
            return 0
        if self.tail < self.head:
            if self.tail == 0 and self.head == self.size:
                return self.head - self.tail + 1
            return self.head - self.tail
        elif self.tail > self.head:
            return self.size - (self.tail - self.head) + 1
        else:
            return self.size


if __name__ == "__main__":
    buf = Buf(size=3)
    for i in range(11):
        buf.append(1)
        print('t', buf.tail, 'h', buf.head)
        print('l', len(buf))