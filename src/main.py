from Lexer import Lexer
from pprint import pprint

lexer = Lexer()
lexer.lex_file('./test/test.plw')
pprint(lexer.tokens)