'''Abstract Syntax Tree and Nodes'''

from Stream import Stream


class Node:
    '''Base Node class'''

    def __init__(self, parent=None, children=list()):
        self.parentnode = parent
        self.childnodes = children
    
    def isleaf(self):
        return not len(self.childnodes)


class Expression(Node):
    '''Expression class for expressions'''

    pass


class Statement(Node):
    '''Statement class for statements'''

    pass


class BinaryExpression(Expression):
    '''BinaryExpression class for binary expressions'''

    def __init__(self, left:Expression, right:Expression, *args, **kwargs):
        self.left = left
        self.right = right
        super().__init__(*args, **kwargs)


class AdditionExpression(BinaryExpression):
    '''AdditionExpression for addition expression'''

    pass


class SubtractionExpression(BinaryExpression):
    '''SubtractionExpression for subtraction expression'''

    pass


class MultiplicationExpression(BinaryExpression):
    '''MultiplicationExpression for multiplication expression'''

    pass


class DivisionExpression(BinaryExpression):
    '''DivisionExpression for division expression'''

    pass


class PowerExpression(BinaryExpression):
    '''PowerExpression for power expression'''

    pass


class AST:
    '''Abstract Syntax Tree class'''

    def parse(self, tokens):
        '''Parse a list of tokens'''

        stream = Stream(tokens)
        while stream.is_not_finished:
            