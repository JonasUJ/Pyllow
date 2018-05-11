'''Stream class'''

class Stream:
    '''Stream class'''

    def __init__(self, iterable):
        self._stream = iterable
        self._i = -1

    @property
    def current(self):
        if self._i < 0:
            return
        return self._stream[self._i]

    @property
    def is_not_finished(self):
        '''If there are more items in the stream'''

        return len(self._stream) - 1 > self._i
        
    def next(self):
        '''Return next item in stream and increase internal counter'''

        if self.is_not_finished:
            self._i += 1
            return self._stream[self._i]

    def prev(self, x=1):
        '''Return previous item in stream and decrease internal counter'''

        if self._i:
            self._i -= x
            return self._stream[self._i]

    def peek_next(self):
        '''Return next item in stream without increasing internal counter'''

        try:
            return self._stream[self._i + 1]
        except IndexError:
            return

    def peek_prev(self, x=1):
        '''Return previous item in stream without decreasing internal counter'''

        if self._i < x:
            return

        try:
            return self._stream[self._i - x]
        except IndexError:
            return

    def skip(self, amount):
        '''Skip `amount` ahead in the and return the item at that index'''
        
        self._i += amount
        try:
            return self._stream[self._i]
        except IndexError:
            return

    def __getitem__(self, index):
        # if type(index) is slice:
        #     return self._stream.__getitem__(index.start:int(index.stop)+1:index.step if index.step else 1)
        return self._stream.__getitem__(index)

    
    