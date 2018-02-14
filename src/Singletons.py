'''Singleton datatypes'''

import datatype.Datatype

class SNull(datatype.Datatype):
    '''Null datatype'''
 
    DATATYPE = 'null'
    VALUE = None
    TOKENS = 'Null'


class STrue(datatype.Datatype):
    '''True datatype'''
 
    DATATYPE = 'true'
    VALUE = True
    tokens = 'True'


class SFalse(datatype.Datatype):
    '''False datatype'''
 
    DATATYPE = 'false'
    VALUE = False
    TOKENS = 'False'