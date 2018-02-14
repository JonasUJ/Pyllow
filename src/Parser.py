'''Main parser and statements'''

import Integer
import String
import Singletons
from Datatype import Datatype

def _any(*args):
    def inner(other):
        return other in args
    return inner

class Statement:
    '''Statement base class'''

    @property
    def BLOCK(self):
        raise NotImplementedError()


    @property
    def KEYWORD(self):
        raise NotImplementedError()


    @property
    def PATTERN(self):
        raise NotImplementedError()


    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs


    def __eq__(self, other):
        return self.KEYWORD == other


    def __repr__(self):
        return f'<{self.__class__.__name__}: _args={self._args}, _kwargs={self._kwargs}>'

    __str__ = __repr__


class KPrint(Statement):
    '''Print statement'''

    KEYWORD = 'print'
    PATTERN = KEYWORD, '(', (Datatype, ','), ')'

    @staticmethod
    def execute(*args):
        print(*args)
    

class Parser:
    '''Main Parser'''

    BLOCKS = '{', '}'
    PARANS = '(', ')'
    LISTS = '[', ']'
    KEYWORDS = KPrint,

    def parse_file(self, path):
        '''Read a file and parse raw text'''

        with open(path) as fp:
            raw = fp.read()

        return self.parse(raw)


    def parse(self, content):
        '''Parse raw text'''

        stmt = Statement
        token = ''
        for i, tok in enumerate(content):
            token += tok

            if token in self.KEYWORDS:
                stmt = self.parseStatement(self.KEYWORDS[token], content[i:])

                token = ''


    def parse_statement(self, stmt, content):
        
        token = ''
        for i, tok in enumerate(content):
            token += tok
            patternindex = 0
            curpattern = stmt.PATTERN[patternindex]

            if len(stmt.PATTERN) - 1 == patternindex:
                return keyw()

            if token == curpattern:

            






'''
if (False == 0) {
    print (3)
    int var = 5 + 3
    print (var)
} 
'''