'''Datatype base class'''

class Datatype:
    '''Datatype base class'''

    @property
    def DATATYPE(self):
        raise  NotImplementedError()

    @property
    def VALUE(self):
        raise  NotImplementedError()

    @property
    def TOKENS(self):
        raise  NotImplementedError()

