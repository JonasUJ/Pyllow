'''Node class and all subclasses'''

from chardef import CD
from Datatype import *
from Error import *

class Node:
    '''Base Node class'''

    _IS_SCOPE = True

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        self.children = kwargs.pop('children', None) or list()
        self.children.extend(args)
        self.position = kwargs.pop('position', None)
        self._scope = dict()

    def pprint_list(self):
        '''Return a Pretty-Printable list'''

        l = list()
        for child in self.children:
            l.append(child)
            cpl = child.pprint_list()
            if cpl:
                l.append(cpl)
        return l

    def add_child(self, child):
        '''Add `child` to Node.children'''

        self.children.append(child)

    def isleaf(self):
        '''A Node is a leaf if it has no children'''

        return not len(self.children)

    def scope_set(self, _id, value):
        '''Change the value of `_id` in the current scope'''

        return self.parent._update_scope(_id, value)

    def scope_get(self, _id, orig=None):
        '''Retrieve `_id` from the current scope'''

        if self._IS_SCOPE and _id in self._scope:
            return self._scope[_id]
        elif self.parent:
            return self.parent.scope_get(_id, orig or self)
        print(orig)
        raise PyllowNameError(f'Name "{_id}" is not defined', orig.position)

    def _update_scope(self, _id, value):
        '''
        Checks, and updates, if this should update it's scope
        because not all Nodes should store a scope (like a loop)
        '''

        if self._IS_SCOPE:
            self._scope[_id] = value
            return value
        return self.parent._update_scope(_id, value)

    def _set_parents(self):
        '''Sets the correct parent for all nodes in the tree'''

        for child in self.children:
            child._set_parents()
            child.parent = self

    def process(self):
        raise NotImplementedError()

    def __repr__(self):
        return f'<{self.__class__.__name__}: len(children)={len(self.children)}>'

    
class TopNode(Node):
    '''The first node in the tree'''

    def process(self):
        self._set_parents()
        i = -1
        while True:
            i += 1
            if len(self.children) == i: break
            new = self.children[i].process()
            if new:
                self.children[i] = new
            else:
                del self.children[i]
                i -= 1


class Expression(Node):
    '''Expression class for expressions'''

    _IS_SCOPE = False

    pass


class Statement(Node):
    '''Statement class for statements'''

    pass


class BinaryExpression(Expression):
    '''BinaryExpression class for binary expressions'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left = self.children[0]
        self.right = self.children[1]

    @classmethod
    def make(cls, lhs, op, rhs, *args, **kwargs):
        return {
            CD.PLUS:AdditionExpression,
            CD.MINUS:SubtractionExpression,
            CD.ASTERISK:MultiplicationExpression,
            CD.DIVISION:DivisionExpression,
            CD.POWER:PowerExpression
        }[op](lhs, rhs, *args, **kwargs)

    def _op(self, lhs, rhs):
        raise NotImplementedError()

    def process(self):
        self.left = self.left.process()
        self.right = self.right.process()
        return self._op(self.left, self.right)

    def __repr__(self):
        return f'<{self.__class__.__name__}: left="{self.left.__class__.__name__}", right="{self.right.__class__.__name__}">'


def exprify(token):
    if not isinstance(token, Expression):
        return MonoExpression(token, position=token.position)
    return token

class MonoExpression(Expression):
    '''For leaf expression nodes'''

    def __init__(self, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = token.value
        self.children = list()
        self.type = token._subtype or token.type

    def process(self):
        return {
            'bool':lambda o: Bool(o.value, o.position),
            'int':lambda o: Integer(o.value, o.position),
            'float':lambda o: Float(o.value, o.position),
            'str':NotImplemented,
            'id':lambda o: o.scope_get(o.value)
        }[self.type](self)

    def __repr__(self):
        return f'<MonoExpression: value="{self.value}">'


class AdditionExpression(BinaryExpression):
    '''AdditionExpression for addition expressions'''

    def _op(self, lhs, rhs):
        return lhs + rhs


class SubtractionExpression(BinaryExpression):
    '''SubtractionExpression for subtraction expressions'''

    def _op(self, lhs, rhs):
        return lhs - rhs


class MultiplicationExpression(BinaryExpression):
    '''MultiplicationExpression for multiplication expressions'''

    def _op(self, lhs, rhs):
        return lhs * rhs


class DivisionExpression(BinaryExpression):
    '''DivisionExpression for division expressions'''

    def _op(self, lhs, rhs):
        return lhs / rhs


class PowerExpression(BinaryExpression):
    '''PowerExpression for power expressions'''

    def _op(self, lhs, rhs):
        return lhs ** rhs


class UnaryExpression(Expression):
    '''For unary expressions'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = kwargs.pop('value', None) or self.children[0]

    def _op(self, value):
        raise NotImplementedError()

    def process(self):
        self.value = self.value.process()
        return self._op(self.value)

    @classmethod
    def make(self, op, *args, **kwargs):
        return {
            CD.NOT:NotExpression,
            CD.PLUS:PositiveExpression,
            CD.MINUS:NegativeExpression
        }[op](*args, **kwargs)

    def __repr__(self):
        return f'<{self.__class__.__name__}: value={self.value}>'


class NotExpression(UnaryExpression):
    '''For `not` expressions'''

    def _op(self, value):
        return value.__not__()


class NegativeExpression(UnaryExpression):
    '''For negative expressions'''

    def _op(self, value):
        return - value


class PositiveExpression(UnaryExpression):
    '''For positive expressions'''

    def _op(self, value):
        return + value


class CallExpression(Expression):
    '''CallExpression for function calls'''

    def __init__(self, identity:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = self.children
        self.id = identity
        self.scope_set(self.id, self)

    def process(self):
        raise NotImplementedError() 


class AssignStatement(Statement):
    '''For variable assignment'''

    _IS_SCOPE = False

    def __init__(self, identity, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = identity

    @property
    def value(self):
        return self.children[0]

    def process(self):
        self.scope_set(self.id, self.value.process())

    def __repr__(self):
        return f'<{self.__class__.__name__}: identity="{self.id}">'


class IfStatement(Statement):
    '''For `if` statements'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        