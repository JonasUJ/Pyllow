'''Stream class'''

class Stream:
    '''Stream class'''

    def __init__(self, iterable):
        self._stream = iterable
        self.i = -1

    @property
    def current(self):
        return self._stream[self.i]

    @property
    def is_not_finished(self):
        '''If there are more items in the stream'''

        return len(self._stream) - 1 > self.i
        
    def next(self):
        '''Return next item in stream'''

        self.i += 1
        return self._stream[self.i]

    def peek_next(self):
        '''Return next item in stream without increasing internal counter'''

        return self._stream[self.i + 1]

    