import unittest

from src.AST import AST, TokenStream
from src.Error import PyllowSyntaxError
from src.Lexer import Lexer, Token
from src.Node import (AdditionExpression, AssignStatement, DivisionExpression,
                      MonoExpression, MultiplicationExpression,
                      NegativeExpression, NotExpression, PositiveExpression,
                      PowerExpression, SubtractionExpression)

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


    # Missing _statement, _call, _if because their logic is not finished



if __name__ == '__main__':
    unittest.main()
