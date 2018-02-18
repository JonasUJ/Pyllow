'''Character definitions'''

_flatten = lambda l: tuple(item for sublist in l for item in sublist)
_flatten_first = lambda l: tuple(sublist[0] for sublist in l)
_split = lambda i, r: tuple((t, r) for t in i)

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
STRING     = '"'
COMMENT    = '#'
ATTRIBUTE  = '.'
OR         = '|'
AND        = '&'
LT         = '<'
GT         = '>'
LE         = '<='
GE         = '>='
EQ         = '=='
NE         = '!='

PRECEDENCE = {
    ASSIGN: 1,
    OR: 2,
    AND: 3,
    LT: 7, GT: 7, LE: 7, GT: 7, EQ: 7, NE: 7,
    PLUS: 10, MINUS: 10,
    ASTERISK: 20, DIVISION: 20,
    POWER: 25
};

OPERATORS = _split('+-*/^', 'op')
ENCAPSULATORS = _split('(){}[]', 'encap')
COMPARISONS = _split(('<', '>', '<=', '>=', '==', '!=', '&', '|'), 'comp')
RESERVED_KEYWORDS = _split(('if', 'else', 'true', 'false', 'null'), 'kwd')
SEPERATOR = _split(',', 'sep')
ALLCHARS = _flatten((OPERATORS, ENCAPSULATORS, COMPARISONS, RESERVED_KEYWORDS, SEPERATOR))
ALLCHARSCLEAN = _flatten_first(ALLCHARS)

NUMBERS = tuple('0123456789')
WHITESPACE = tuple(' \n\r\t\v')