from fifo import Fifo
import array


class Buf(Fifo):
    def __init__(self, *iter, size=None):
        self.data = array.array('H')
        if size:
            for i in range(size):
                self.data.append(0)
            self.size = size
            self.head = 0
        else:
            for iterables in iter:
                for element in iterables:
                    self.data.append(element)
            self.size = sum(len(i) for i in iter)
            self.head = self.size - 1
        self.tail = 0
        self.dc = 0
        self.count = 0

    def get(self):
        self.count += 1
        return super().get()
    
    def append(self, value):
        new_head = (self.head + 1) % self.size
        if new_head == self.tail:
            self.tail = (self.tail + 1) % self.size
        self.head = new_head
        self.data[new_head] = value

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
                raise IndexError('No support for negative indices.')
            true_index = self.get_real_index(index)
            return self.data[true_index]

        elif isinstance(index, slice):
            if (index.start < 0) or (index.stop < 0):
                raise IndexError('No support for negative indices.')
            start = self.get_real_index(index.start)
            stop = self.get_real_index(index.stop)
            if (index.start < index.stop) and not index.start:
                length = stop - start
                self.tail += length
                self.count += length
            return Buf(self.data[start:stop])
        raise TypeError('Only ints and slices supported.')
        
    def __len__(self):
        if self.tail < self.head:
            return self.head - self.tail + 1
        elif self.tail > self.head:
            return self.size - (self.tail - self.head) + 1
        else:
            return 0
        

if __name__ == "__main__":
    buf = Buf([1,2,3,4,5,6,7,8,9,10])
    buf2 = Buf([10,9,8,7,6,5,4,3,2,1])
    for i in range(15):
        buf.append(buf2.get())
        print(buf.tail, buf.head)
    print(buf.data)
    print(len(buf))