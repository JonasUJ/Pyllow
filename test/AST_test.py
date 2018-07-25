import unittest

from src.AST import AST, TokenStream
from src.chardef import CD
from src.Error import PyllowSyntaxError
from src.Lexer import Lexer, Token
from src.Node import (AdditionExpression, AndExpression, AssignStatement,
                      BlockNode, DivisionExpression, EqualExpression,
                      GreaterThanEqualExpression, GreaterThanExpression,
                      IfStatement, LessThanEqualExpression, LessThanExpression,
                      MonoExpression, MultiplicationExpression,
                      NegativeExpression, NotEqualExpression, NotExpression,
                      OrExpression, PositiveExpression, PowerExpression,
                      SubtractionExpression)

POSITION = (1, 0, 'test')
KWARGS = {
    'tokentype': 'num',
    'subtype': 'int',
    'value': '0',
    'identity': 'id',
    'position': POSITION
}


def make_tree(node_and_children):
    nodeclass, children = node_and_children
    if isinstance(children, tuple) and children[1]:
        return nodeclass(children=[make_tree(child) for child in children])
    elif isinstance(children, tuple):
        return nodeclass(children=[make_tree(children)], **KWARGS)
    return nodeclass(**KWARGS)


class ASTTest(unittest.TestCase):

    def setUp(self):
        self.tree = AST(())

    def tearDown(self):
        del self.tree

    def set_stream(self, raw):
        lexer = Lexer()
        lexed = lexer.lex(raw)
        self.tree._stream = TokenStream(lexed)
        self.tree._stream.next()

    def test__accept(self):
        self.set_stream('A B 1 2')
        self.assertTrue(self.tree._accept('A', attr='value'))
        self.assertFalse(self.tree._accept('A', attr='value'))
        self.assertTrue(self.tree._accept('id'))
        self.assertFalse(self.tree._accept('id'))
        self.assertTrue(self.tree._accept('id', 'num'))
        self.assertFalse(self.tree._accept('id', 'num', attr='value'))
        self.assertTrue(self.tree._accept('B', '2', attr='value'))

    def test__expect(self):
        self.set_stream('A B 1 2')
        self.assertTrue(self.tree._expect('A', attr='value'))
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expect('A', attr='value')
        self.assertTrue(self.tree._expect('id'))
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expect('id')
        self.assertTrue(self.tree._expect('id', 'num'))
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expect('id', 'num', attr='value')
        self.assertTrue(self.tree._expect('B', '2', attr='value'))

    def test__expression_simpel(self):
        self.set_stream('1 + 2 - 3')
        structure = make_tree(
            (SubtractionExpression, (
                (AdditionExpression, (
                    (MonoExpression, None),
                    (MonoExpression, None)
                )),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)
        
    def test__expression_precedence(self):
        self.set_stream('1 + 2 * 3')
        structure = make_tree(
            (AdditionExpression, (
                (MonoExpression, None),
                (MultiplicationExpression, (
                    (MonoExpression, None),
                    (MonoExpression, None)
                ))
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_precedence_arg(self):
        self.set_stream('1 ^ 2 * 3')
        structure = make_tree(
            (PowerExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current, precedence=22)
        self.assertEqual(expr, structure)

    def test__expression_unary(self):
        self.set_stream('1 - - 2')
        structure = make_tree(
            (SubtractionExpression, (
                (MonoExpression, None),
                (NegativeExpression, (MonoExpression, None))
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        from pprint import pprint
        print('struct')
        pprint(structure.pprint_list())
        print('expr')
        pprint(expr.pprint_list())
        self.assertEqual(expr, structure)

    def test__expression_singleparen(self):
        self.set_stream('(1) + (2)')
        structure = make_tree(
            (AdditionExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_singleparen_unary(self):
        self.set_stream('(1) + (-2)')
        structure = make_tree(
            (AdditionExpression, (
                (MonoExpression, None),
                (NegativeExpression, (MonoExpression, None))
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_double_and_tripleparen(self):
        self.set_stream('((1)) + (((2)))')
        structure = make_tree(
            (AdditionExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_double_and_tripleparen_unary(self):
        self.set_stream('(1) + (-2)')
        structure = make_tree(
            (AdditionExpression, (
                (MonoExpression, None),
                (NegativeExpression, (MonoExpression, None))
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_paren_precedence(self):
        self.set_stream('(1 + 2) * 3')
        structure = make_tree(
            (MultiplicationExpression, (
                (AdditionExpression, (
                    (MonoExpression, None), 
                    (MonoExpression, None)
                )),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_paren_nesting(self):
        self.set_stream('(1 + (2 - 3)) * 4')
        structure = make_tree(
            (MultiplicationExpression, (
                (AdditionExpression, (
                    (MonoExpression, None),
                    (SubtractionExpression, (
                        (MonoExpression, None),
                        (MonoExpression, None)
                    ))
                )),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_paren_operation(self):
        self.set_stream('(1 - 2) * (3 + 4)')
        structure = make_tree(
            (MultiplicationExpression, (
                (SubtractionExpression, (
                    (MonoExpression, None),
                    (MonoExpression, None)
                )),
                (AdditionExpression, (
                    (MonoExpression, None),
                    (MonoExpression, None)
                ))
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_addition(self):
        self.set_stream('1 + 2')
        structure = make_tree(
            (AdditionExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_subtraction(self):
        self.set_stream('1 - 2')
        structure = make_tree(
            (SubtractionExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_multiplication(self):
        self.set_stream('1 * 2')
        structure = make_tree(
            (MultiplicationExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_division(self):
        self.set_stream('1 / 2')
        structure = make_tree(
            (DivisionExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_power(self):
        self.set_stream('1 ^ 2')
        structure = make_tree(
            (PowerExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_EQ(self):
        self.set_stream('1 == 2')
        structure = make_tree(
            (EqualExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_NE(self):
        self.set_stream('1 != 2')
        structure = make_tree(
            (NotEqualExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_AND(self):
        self.set_stream('1 & 2')
        structure = make_tree(
            (AndExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_OR(self):
        self.set_stream('1 | 2')
        structure = make_tree(
            (OrExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_GT(self):
        self.set_stream('1 > 2')
        structure = make_tree(
            (GreaterThanExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_LT(self):
        self.set_stream('1 < 2')
        structure = make_tree(
            (LessThanExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_GE(self):
        self.set_stream('1 >= 2')
        structure = make_tree(
            (GreaterThanEqualExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_LE(self):
        self.set_stream('1 <= 2')
        structure = make_tree(
            (LessThanEqualExpression, (
                (MonoExpression, None),
                (MonoExpression, None)
            ))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_negative(self):
        self.set_stream('-1')
        structure = make_tree(
            (NegativeExpression, (MonoExpression, None))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_positive(self):
        self.set_stream('+1')
        structure = make_tree(
            (PositiveExpression, (MonoExpression, None))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_not(self):
        self.set_stream('!1')
        structure = make_tree(
            (NotExpression, (MonoExpression, None))
        )
        expr = self.tree._expression(self.tree._stream.current)
        self.assertEqual(expr, structure)

    def test__expression_raises_missing(self):
        self.set_stream('1 +')
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expression(self.tree._stream.current)

    def test__expression_raises_double(self):
        self.set_stream('1 * * 2')
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expression(self.tree._stream.current)

    def test__expression_raises_empty_paren(self):
        self.set_stream('1 * () * 2')
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expression(self.tree._stream.current)

    def test__expression_raises_invalid_unary(self):
        self.set_stream('* 2')
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expression(self.tree._stream.current)

    def test__expression_raises_invalid_token(self):
        self.set_stream('if + 2')
        with self.assertRaises(PyllowSyntaxError):
            self.tree._expression(self.tree._stream.current)

    def test__assignment(self):
        self.set_stream('id = expr')
        structure = make_tree(
            (AssignStatement, (MonoExpression, None))
        )
        expr = self.tree._assignment()
        self.assertEqual(expr, structure)
        self.assertTrue(expr.id, 'id')

    def test__assignment_no_id(self):
        self.set_stream('1')
        self.assertFalse(self.tree._assignment())

    def test__assignment_no_assign(self):
        self.set_stream('id')
        self.assertFalse(self.tree._assignment())

    def test__assignment_raises_no_expression(self):
        self.set_stream('id = ')
        with self.assertRaises(PyllowSyntaxError):
            self.tree._assignment()
        
    def test__assignment_raises_invalid_expression(self):
        self.set_stream('id = if')
        with self.assertRaises(PyllowSyntaxError):
            self.tree._assignment()

    def test__get_block(self):
        self.set_stream('{assign1 = 1 assign2 = 2}')
        structure = make_tree(
            (BlockNode, (
                (AssignStatement, (MonoExpression, None)),
                (AssignStatement, (MonoExpression, None))
            ))
        )
        block = self.tree._get_block()
        self.assertEqual(block, structure)

    def test__if(self):
        self.set_stream('if true {}')
        self.tree._accept(CD.IF, attr='value')
        expr = self.tree._if()
        self.assertFalse(expr.alt)
        self.assertTrue(expr.condition.value)

    def test__if_block(self):
        self.set_stream('if true {test = 0}')
        self.tree._accept(CD.IF, attr='value')
        structure = make_tree(
            (AssignStatement, (MonoExpression, None))
        )
        expr = self.tree._if()
        self.assertEqual(expr.block.children[0], structure)

    def test__if_condition(self):
        self.set_stream('if 1 == 0 | 1 != 0 {}')
        self.tree._accept(CD.IF, attr='value')
        structure = make_tree(
            (OrExpression, (
                (EqualExpression, (
                    (MonoExpression, None),
                    (MonoExpression, None))
                ),
                (NotEqualExpression, (
                    (MonoExpression, None),
                    (MonoExpression, None))
                )
            ))
        )
        expr = self.tree._if()
        self.assertEqual(expr.condition, structure)

    def test__if_else(self):
        self.set_stream('if true {} else {test = 0}')
        self.tree._accept(CD.IF, attr='value')
        structure = make_tree(
            (AssignStatement, (MonoExpression, None))
        )
        expr = self.tree._if()
        self.assertEqual(expr.alt.children[0], structure)

    def test__if_else_if(self):
        self.set_stream('if true {} else if true {test = 0}')
        self.tree._accept(CD.IF, attr='value')
        structure = make_tree(
            (AssignStatement, (MonoExpression, None))
        )
        expr = self.tree._if()
        self.assertEqual(expr.alt.block.children[0], structure)

    
        

    # Missing _statement, _call because their logic is not finished



if __name__ == '__main__':
    unittest.main()
