from Lexer import Lexer
from pprint import pprint

lexer = Lexer()
lexer.lex_file('./test.slp')
pprint(lexer.tokens)