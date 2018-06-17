'''Character definitions'''

_flatten = lambda l: tuple(item for sublist in l for item in sublist)
_flatten_first = lambda l: tuple(sublist[0] for sublist in l)
_split = lambda l, r: tuple((t, r) for t in l)
_double = lambda l: tuple((t, t) for t in l)

class CD:
    PLUS       = '+'
    MINUS      = '-'
    ASTERISK   = '*'
    DIVISION   = '/'
    POWER      = '^'
    ASSIGN     = '='
    LPAREN     = '('
    RPAREN     = ')'
    LISTSTART  = '['
    LISTEND    = ']'
    BLOCKSTART = '{'
    BLOCKEND   = '}'
    ATTRIBUTE  = '.'
    OR         = '|'
    AND        = '&'
    LT         = '<'
    GT         = '>'
    LE         = '<='
    GE         = '>='
    EQ         = '=='
    NE         = '!='
    NOT        = '!'
    IF         = 'if'
    ELSE       = 'else'
    TRUE       = 'true'
    FALSE      = 'false'
    NULL       = 'null'


PRECEDENCE = {
    CD.OR: 2,
    CD.AND: 3,
    CD.NOT: 4,
    CD.LT: 7, CD.GT: 7, CD.LE: 7, CD.GT: 7, CD.EQ: 7, CD.NE: 7,
    CD.PLUS: 10, CD.MINUS: 10,
    CD.ASTERISK: 20, CD.DIVISION: 20,
    CD.POWER: 25,
    CD.ATTRIBUTE: 30
}

RIGHT_ASSOC = (
    CD.POWER,
)

OPERATORS = _split(('+', '-', '*', '/', '^', '<', '>', '<=', '>=', '==', '!=', '&', '|', '!', '.'), 'op')
ENCAPSULATORS = ('(', 'LPAREN'), (')', 'RPAREN'), ('{', 'BLOCKSTART'), ('}', 'BLOCKEND'), ('[', 'LISTSTART'), (']', 'LISTEND')
RESERVED_KEYWORDS = _double(('if', 'else', 'null'))
MISC = ((',', 'sep'), ('true', 'bool'), ('false', 'bool'), ('=', 'assign'), ('EOF', 'EOF'))
ALLCHARS = _flatten((OPERATORS, ENCAPSULATORS, RESERVED_KEYWORDS, MISC))
ALLCHARSCLEAN = _flatten_first(ALLCHARS)

NUMBERS = tuple('0123456789')
WHITESPACE = tuple(' \n\r\t\v')
COMMENT = '#'
STRING = '"'