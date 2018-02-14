'''Integer type'''

import Datatype.Datatype

class Integer(Datatype.Datatype):
    '''Integer datatype'''

    DATATYPE = 'int'
    VALUE = 0
    TOKENS = '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'

    def __init__(self, value):
        self.VALUE = value
