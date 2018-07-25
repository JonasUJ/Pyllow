import unittest
from unittest.mock import MagicMock

from src.chardef import CD
from src.Datatype import Bool, Float, Integer
from src.Error import PyllowNameError, PyllowSyntaxError
from src.Lexer import Lexer, Token
from src.Node import (AdditionExpression, AssignStatement, BinaryExpression,
                      BlockNode, DivisionExpression, EqualExpression,
                      IfStatement, MonoExpression, MultiplicationExpression,
                      NegativeExpression, Node, NotEqualExpression,
                      NotExpression, PositiveExpression, PowerExpression,
                      SubtractionExpression, TopNode, UnaryExpression, exprify)

POSITION = (1, 0, 'test')
LEFT = exprify(Token(value='1', type='num', subtype='int', position=POSITION))
RIGHT = exprify(Token(value='2', type='num', subtype='int', position=POSITION))
BINEXPR = BinaryExpression(LEFT, RIGHT)
TRUTHY = EqualExpression(LEFT, LEFT)
FALSY = NotEqualExpression(LEFT, LEFT)

TOKEN = Token(value='test', type='id', position=POSITION)
MONOEXPRESSION = MonoExpression.make(TOKEN)


class NodeTest(unittest.TestCase):

    def setUp(self):
        self.node = Node(parent=TopNode())

    def tearDown(self):
        del self.node

    def test_add_child(self):
        self.node.add_child(BINEXPR)
        self.assertEqual(self.node.children[0], BINEXPR)

    def test_isleaf(self):
        self.assertTrue(self.node.isleaf())
        self.node.add_child(BINEXPR)
        self.assertFalse(self.node.isleaf())

    def test_scope_set_is_scope(self):
        self.node.scope_set('test', BINEXPR)
        print(self.node.parent._scope)
        self.assertEqual(self.node._scope['test'], BINEXPR)

    def test_scope_set_is_not_scope(self):
        self.node._IS_SCOPE = False
        self.node.scope_set('test', BINEXPR)
        self.assertEqual(self.node.parent._scope['test'], BINEXPR)

    def test_scope_get_is_scope(self):
        self.node._scope['test'] = BINEXPR
        self.assertEqual(self.node.scope_get('test'), BINEXPR)
        
    def test_scope_get_is_scope_not_defined(self):
        self.node.parent._scope['test'] = BINEXPR
        self.assertEqual(self.node.scope_get('test'), BINEXPR)

    def test_scope_get_is_not_scope(self):
        self.node._IS_SCOPE = False
        self.node.parent._scope['test'] = BINEXPR
        self.assertEqual(self.node.scope_get('test'), BINEXPR)

    def test_scope_get_raises(self):
        with self.assertRaises(PyllowNameError):
            self.node.scope_get('test')

    def test__update_scope_is_scope(self):
        self.assertEqual(self.node._update_scope('test', BINEXPR), BINEXPR)
        self.assertEqual(self.node._scope['test'], BINEXPR)

    def test__update_scope_is_not_scope(self):
        self.node._IS_SCOPE = False
        self.assertEqual(self.node._update_scope('test', BINEXPR), BINEXPR)
        self.assertEqual(self.node.parent._scope['test'], BINEXPR)

    def test__set_parents(self):
        self.node.add_child(Node())
        self.node._set_parents()
        self.assertEqual(self.node.children[0].parent, self.node)

    def test___eq__(self):
        self.node.add_child(BINEXPR)
        self.assertEqual(self.node, Node(children=[BINEXPR]))

    def test___ne__(self):
        self.node.add_child(BINEXPR)
        self.assertNotEqual(self.node, Node(children=[BINEXPR, BINEXPR]))


class TopNodeTest(NodeTest):

    # TopNode currently has one method `process` 
    # and I don't feel like it needs testing
    pass


class BinaryExpressionTest(unittest.TestCase):

    def test_make(self):
        self.assertEqual(BinaryExpression.make(LEFT, CD.PLUS, RIGHT), AdditionExpression(LEFT, RIGHT))
        self.assertEqual(BinaryExpression.make(LEFT, CD.MINUS, RIGHT), SubtractionExpression(LEFT, RIGHT))
        self.assertEqual(BinaryExpression.make(LEFT, CD.ASTERISK, RIGHT), MultiplicationExpression(LEFT, RIGHT))
        self.assertEqual(BinaryExpression.make(LEFT, CD.DIVISION, RIGHT), DivisionExpression(LEFT, RIGHT))
        self.assertEqual(BinaryExpression.make(LEFT, CD.POWER, RIGHT), PowerExpression(LEFT, RIGHT))
    
    def test_make_raises(self):
        with self.assertRaises(KeyError):
            BinaryExpression.make(LEFT, 'test', RIGHT) # Will break if a 'test' symbol exists


class exprifyTest(unittest.TestCase):

    def test_exprify(self):
        self.assertEqual(exprify(MONOEXPRESSION), MONOEXPRESSION)
        self.assertEqual(exprify(TOKEN), MONOEXPRESSION)
        with self.assertRaises(PyllowSyntaxError):
            exprify(Token(value='if', type='if', position=POSITION))


class MonoExpressionTest(unittest.TestCase):

    def test_process(self):
        self.assertEqual(MonoExpression.make(Token(value='true', type='bool', position=POSITION)).process(),
            Bool('true', position=POSITION))
        self.assertEqual(MonoExpression.make(Token(value='1', type='int', position=POSITION)).process(),
            Integer(value='1', position=POSITION))
        self.assertEqual(MonoExpression.make(Token(value='1.0', type='float', position=POSITION)).process(),
            Integer(value='1.0', position=POSITION))

    def test_process_id(self):
        top = TopNode()
        expr = MonoExpression.make(Token(value='test', type='id', position=POSITION), parent=top)
        with self.assertRaises(PyllowNameError):
            expr.process()
        expr.scope_set('test', 'test')
        self.assertEqual(expr.process(), 'test')

    def test_process_raises(self):
        with self.assertRaises(PyllowSyntaxError):
            MonoExpression.make(Token(value='test', type='test', position=POSITION)).process()
        
        
class BinaryExpressionSubclassesTest(unittest.TestCase):

    def test__op(self):
        self.assertEqual(AdditionExpression(4, 2)._op(4, 2), 6)
        self.assertEqual(SubtractionExpression(4, 2)._op(4, 2), 2)
        self.assertEqual(MultiplicationExpression(4, 2)._op(4, 2), 8)
        self.assertEqual(DivisionExpression(4, 2)._op(4, 2), 2.0)
        self.assertEqual(PowerExpression(4, 2)._op(4, 2), 16)


class UnaryExpressionTest(unittest.TestCase):

    def test_make(self):
        self.assertEqual(UnaryExpression.make(CD.NOT, RIGHT), NotExpression(RIGHT))
        self.assertEqual(UnaryExpression.make(CD.PLUS, RIGHT), PositiveExpression(RIGHT))
        self.assertEqual(UnaryExpression.make(CD.MINUS, RIGHT), NegativeExpression(RIGHT))


class UnaryExpressionSubclassesTest(unittest.TestCase):

    def test__op(self):
        one = Integer(1, POSITION)
        one.__not__ = MagicMock()
        NotExpression(one)._op(one)
        one.__not__.assert_called_once_with()
        self.assertEqual(NegativeExpression(1)._op(1), -1)
        self.assertEqual(PositiveExpression(1)._op(1), +1)


class AssignStatementTest(unittest.TestCase):

    def setUp(self):
        self.node = AssignStatement('test', LEFT, parent=TopNode())

    def tearDown(self):
        del self.node

    def test_value(self):
        self.assertEqual(self.node.value, LEFT)

    def test_process(self):
        self.node.process()
        self.assertEqual(self.node.parent._scope['test'], LEFT.process())


class IfStatementTest(unittest.TestCase):

    def setUp(self):
        self.node = IfStatement(EqualExpression(exprify(Token(value='1', type='num', subtype='int', position=POSITION)), exprify(Token(value='2', type='num', subtype='int', position=POSITION))),
            BlockNode(AssignStatement('test', LEFT)),
            IfStatement(
                EqualExpression(exprify(Token(value='1', type='num', subtype='int', position=POSITION)), exprify(Token(value='2', type='num', subtype='int', position=POSITION))),
                BlockNode(AssignStatement('test', LEFT)),
                IfStatement(
                    NotEqualExpression(exprify(Token(value='1', type='num', subtype='int', position=POSITION)), exprify(Token(value='2', type='num', subtype='int', position=POSITION))),
                    BlockNode(AssignStatement('test', RIGHT)), False)
            ),
        parent=TopNode())
    
    def tearDown(self):
        del self.node
        
    def test_condition(self):
        self.assertEqual(self.node.condition.process(), False)

    def test_block(self):
        self.node.block.process()
        self.assertEqual(self.node.parent._scope['test'], LEFT.process())
    
    def test_logic(self):
        self.node.process()
        self.assertEqual(self.node.parent._scope['test'], RIGHT.process())
        

if __name__ == '__main__':
    unittest.main()
