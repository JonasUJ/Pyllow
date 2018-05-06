'''Main lexer and tokens'''

from os.path import realpath

from chardef import COMMENT, STRING, NUMBERS, ALLCHARS, ALLCHARSCLEAN, WHITESPACE
from Stream import Stream


class RawStream(Stream):
    '''RawStream for ASCII source code'''

    def __init__(self, *args,  path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._lineno = 1
        self._columnno = -1
        self.path = path

    def next(self):
        self._columnno += 1
        if self.current == '\n':
            self._lineno += 1
            self._columnno = 0
        super().next()

    def prev(self):
        super().prev()
        self._columnno -= 1
        if self.current == '\n':
            self._lineno -= 1
            self._columnno = 0

    def position(self, backtrack_lineno=0, backtrack_columnno=0):
        return self._lineno - backtrack_lineno, self._columnno - backtrack_columnno, self.path


class Token:
    '''Token class'''
    
    def __init__(self, **kwargs):
        self.position = kwargs.pop('position')
        self.type = kwargs.pop('type')
        self.value = kwargs.pop('value')
        self._subtype = kwargs.pop('subtype', None)

    def __repr__(self):
        return f'<{self.__class__.__name__}: position={self.position}, type="{self.type}", value="{self.value}">'

    __str__ = __repr__


class Lexer:
    '''Lexer class'''

    tokens = list()
    tok = str()

    def add_token(self, **kwargs):
        token = Token(**kwargs)
        self.tokens.append(token)
        self.tok = str()
        self.couldbenum = True
        print('added:', token)

    def lex_file(self, path):
        '''Read a file and lex raw text'''

        with open(path) as fp:
            raw = fp.read()
            path = realpath(fp.name)

        return self.lex(raw, path=path)

    def lex(self, raw, path=None):
        '''Lex raw text'''

        self.tokens.clear()

        isstring = False
        iscomment = False
        isdecimal = False
        self.couldbenum = True

        stream = RawStream(raw + ' EOF ', path=path or '_main_')
        while stream.is_not_finished:
            stream.next()

            if stream.current == '\n':
                iscomment = False
                
            if (stream.current in WHITESPACE and not isstring) and not self.tok or iscomment:
                continue

            if stream.current == STRING:
                isstring = not isstring
                if not isstring:
                    self.add_token(position=stream.position(), type='str', value=self.tok)
                self.tok = str()
                continue
                
            elif self.tok and (stream.current in WHITESPACE or stream.current in ALLCHARSCLEAN) \
                    and self.tok + stream.current not in ALLCHARSCLEAN and not isstring \
                    and not isdecimal:
                self.add_token(position=stream.position(), type='id', value=self.tok)
                if stream.current in ALLCHARSCLEAN and stream.current + stream.peek_next() not in ALLCHARSCLEAN:
                    t = ALLCHARS[ALLCHARSCLEAN.index(stream.current)]
                    stream.next()
                    self.add_token(position=stream.position(), type=t[1], value=t[0])
                stream.prev()
                continue

            self.tok += stream.current

            print('chr:', stream.current, '| tok:', self.tok+'|')

            if len(self.tok) == 1 and not self.tok.isdigit():
                self.couldbenum = False

            if isstring:
                continue

            if stream.current in NUMBERS and stream.peek_next() not in NUMBERS and self.couldbenum:
                if stream.peek_next() == '.' and not isdecimal:
                    isdecimal = True
                else:
                    self.add_token(
                        position=stream.position(),
                        type='num',
                        value=self.tok,
                        subtype = 'float' if isdecimal else 'int')
                    isdecimal = False

            elif self.tok == COMMENT:
                iscomment = True
                self.tok = str()

            elif self.tok in ALLCHARSCLEAN and self.tok + stream.peek_next() not in ALLCHARSCLEAN:
                t = ALLCHARS[ALLCHARSCLEAN.index(self.tok)]
                self.add_token(position=stream.position(), type=t[1], value=t[0])

        return self.tokens
                