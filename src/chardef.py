'''Character definitions'''

flatten = lambda l: tuple(item for sublist in l for item in sublist)
flatten_first = lambda l: tuple(sublist[0] for sublist in l)
split = lambda i, r: tuple((t, r) for t in i)

OPERATORS = split('+-*/^', 'op')
ENCAPSULATORS = split('(){}[]', 'encap')
COMPARISON = split(('<', '>', '<=', '>=', '==', '&', '|'), 'comp')
RESERVED_KEYWORDS = split(('if', 'else', 'true', 'false', 'null'), 'kwd')
SEPERATOR = split(',', 'sep')
ALLCHARS = flatten((OPERATORS, ENCAPSULATORS, COMPARISON, RESERVED_KEYWORDS, SEPERATOR))
ALLCHARSCLEAN = flatten_first(ALLCHARS)

NUMBERS = tuple('0123456789')
WHITESPACE = tuple(' \n\r\t\v')
COMMENT = '#'