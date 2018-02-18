'''Main lexer and tokens'''

from chardef import COMMENT, STRING, NUMBERS, ALLCHARS, ALLCHARSCLEAN, WHITESPACE
from Stream import Stream


class RawStream(Stream):
    '''RawStream for ASCII source code'''

    def __init__(self, *args, **kwargs):
        self._lineno = 1
        self._columnno = -1
        super().__init__(*args, **kwargs)

    def next(self):
        self._columnno += 1
        if self.current == '\n':
            self._lineno += 1
            self._columnno = 0
        super().next()

    def position(self):
        return (self._columnno, self._lineno)


class Token:
    '''Token class'''
    def __init__(self, **kwargs):
        self.position = kwargs.pop('position')
        self.role = kwargs.pop('role')
        self.value = kwargs.pop('value')

    def __repr__(self):
        return f'<{self.__class__.__name__}: position={self.position}, role="{self.role}", value="{self.value}">'

    __str__ = __repr__


class Lexer:
    '''Lexer class'''

    tokens = list()
    tok = str()

    def add_token(self, **kwargs):
        token = Token(**kwargs)
        self.tokens.append(token)
        self.tok = str()
        print('added:', token)

    def lex_file(self, path):
        '''Read a file and lex raw text'''

        with open(path) as fp:
            raw = fp.read()

        return self.lex(raw)

    def lex(self, raw):
        '''Lex raw text'''

        isstring = False
        iscomment = False

        stream = RawStream(raw)
        while stream.is_not_finished:
            stream.next()

            if stream.current == '\n':
                iscomment = False
                continue
            elif (stream.current in WHITESPACE and not isstring) and not self.tok or iscomment:
                continue

            if stream.current == STRING:
                isstring = not isstring
                if not isstring:
                    self.add_token(position=stream.position(), role='str', value=self.tok)
                self.tok = str()
                continue

            elif self.tok and (stream.current in WHITESPACE or stream.current in ALLCHARSCLEAN) and not isstring:
                self.add_token(position=stream.position(), role='id', value=self.tok)
                continue

            self.tok += stream.current

            print('chr:', stream.current, '| tok:', self.tok+'|')

            if isstring:
                continue

            if stream.current in NUMBERS and stream.peek_next() not in NUMBERS:
                self.add_token(position=stream.position(), role='num', value=self.tok)
                continue

            elif self.tok == COMMENT:
                iscomment = True
                self.tok = str()
                continue

            elif self.tok in ALLCHARSCLEAN:
                t = ALLCHARS[ALLCHARSCLEAN.index(self.tok)]
                self.add_token(position=stream.position(), role=t[1], value=t[0])

                