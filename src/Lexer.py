'''Main lexer and tokens'''

from chardef import *


class Token:
    '''Token class'''
    def __init__(self, **kwargs):
        self.line = kwargs.pop('line')
        self.role = kwargs.pop('role')
        self.value = kwargs.pop('value')

    def __repr__(self):
        return f'<{self.__class__.__name__}: line={self.line}, role="{self.role}", value="{self.value}">'

    __str__ = __repr__


class Lexer:
    '''Lexer class'''

    tokens = list()

    def add(self, item):
        print('added:', item)
        self.tokens.append(item)

    def lex_file(self, path):
        '''Read a file and lex raw text'''

        with open(path) as fp:
            raw = fp.read()

        return self.lex(raw)

    def lex(self, raw):
        '''Lex raw text'''

        isstring = False
        iscomment = False
        line = 1
        tok = str()
        for i, char in enumerate(raw + ' EOF'):

            if char == '\n':
                line += 1
                iscomment = False
                continue
            elif (char in WHITESPACE and not isstring) and not tok or iscomment:
                continue

            if char == '"':
                isstring = not isstring
                if not isstring:
                    token = Token(line=line, role='str', value=tok)
                    self.add(token)
                tok = str()
                continue

            elif tok and (char in WHITESPACE or char in ALLCHARSCLEAN) and not isstring:
                token = Token(line=line, role='id', value=tok)
                self.add(token)
                tok = str()
                continue

            tok += char

            print('chr:', char, '| tok:', tok+'|')

            if isstring:
                continue

            if char in NUMBERS and raw[i+1] not in NUMBERS:
                token = Token(line=line, role='num', value=tok)
                self.add(token)
                tok = str()
                continue

            elif tok == COMMENT:
                iscomment = True
                tok = str()
                continue

            elif tok in ALLCHARSCLEAN:
                t = ALLCHARS[ALLCHARSCLEAN.index(tok)]
                token = Token(line=line, role=t[1], value=t[0])
                self.add(token)
                tok = str()

                