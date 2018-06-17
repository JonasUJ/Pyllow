'''Main lexer and tokens'''

from os.path import realpath

from .chardef import COMMENT, STRING, NUMBERS, ALLCHARS, ALLCHARSCLEAN, WHITESPACE
from .Stream import Stream


class RawStream(Stream):
    '''
    RawStream for ASCII/UTF-8 source code

    Parameters
    ----------
    path : str
        The path to the file
    newlinechar : str
        The character that introduces a new line, default is '\n'
        cannot be multiple characters like '\r\n' or '\n\r'
    '''

    def __init__(self, *args,  path=None, newlinechar='\n', **kwargs):
        super().__init__(*args, **kwargs)
        self._lineno = 1
        self._columnno = -1
        self.path = path
        self.newlinechar = newlinechar

    def next(self):
        self._columnno += 1
        if self.current == self.newlinechar:
            self._lineno += 1
            self._columnno = 0
        super().next()
        return self._stream[self._i] if self.is_not_finished else None

    def prev(self):
        super().prev()
        self._columnno -= 1
        if self.current == self.newlinechar:
            self._lineno -= 1
            _x = 1
            cur = self._stream[self._i - _x]
            while cur != self.newlinechar and _x < self._i:
                _x += 1
                cur = self._stream[self._i - _x]
            self._columnno = _x
        return self._stream[self._i] if self._i > 0 else None

    def skip(self, amount):
        '''Skip `amount` items forward and return the current item'''

        if amount < 0:
            raise ValueError('Amount must be greater than 0')
        
        for _ in range(amount):
            self.next()
        return self.current

    def position(self):
        return self._lineno, self._columnno, self.path


class Token:
    '''
    Token class that contains information on tokens in
    the source code

    Parameters
    ----------
    position : tuple
        A 3 length tuple with the line number, column number and filename
        of the token
    type : str
        Type of the token
    subtype : str
        Subtype of the token, for when the type is not specific enough
        e.g. 'num' could be either 'int' or 'float'
    value : str
        The value of the token
    '''
    
    def __init__(self, **kwargs):
        self.position = kwargs.pop('position')
        self.type = kwargs.pop('type')
        self.value = kwargs.pop('value')
        self._subtype = kwargs.pop('subtype', None)

    def __repr__(self):
        return f'<{self.__class__.__name__}: position={self.position}, type="{self.type}", value="{self.value}">'

    def __eq__(self, other):
        return self.position == other.position and \
            self.type == other.type and \
            self.value == other.value and \
            self._subtype == other._subtype

    def __ne__(self, other):
        return not self.__eq__(other)

class Lexer:
    '''Lexer class'''

    tokens = list()
    tok = str()

    def add_token(self, **kwargs):
        token = Token(**kwargs)
        self.tokens.append(token)
        self.tok = str()
        self.couldbenum = True
        #print('added:', token)

    def lex_file(self, path, error_path=None):
        '''
        Read a file and lex raw text
        
        Parameters
        ----------
        path
            Location of file
        error_path
            The path saved to every token, leave out to use `path`
        '''

        with open(path) as fp:
            raw = fp.read()
            path = realpath(fp.name)

        error_path = error_path or path

        return self.lex(raw, path=error_path)

    def lex(self, raw, path=None):
        '''
        Lex raw text
        
        Parameters
        ----------
        raw
            String of characters
        path
            The path saved to every token in their position attribute

        Returns
        -------
        list : List[Token]
            A list of `Token`s
        '''

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

            #print('chr:', stream.current, '| tok:', self.tok+'|')

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
                