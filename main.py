from src.Lexer import Lexer
from src.AST import AST
from pprint import pprint

lexer = Lexer()
lexer.lex_file('test/Lexer_test.plw')
pprint(lexer.tokens)

tree = AST(lexer.tokens)
if not tree.parse():
#    exit()
    pass
print('-'*100)
#pprint(tree.tree.pprint_list(), indent=4)
print('-'*100)
tree.execute()
pprint(tree.tree._scope)
print('-'*100)
pass