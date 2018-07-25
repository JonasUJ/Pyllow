'''Node class and all subclasses'''

from .chardef import CD
from .Datatype import Float, Integer, Bool
from .Error import PyllowNameError, PyllowSyntaxError

class Node:
    '''
    Base Node class that makes up all of the tree
    Used for subclassing and testing, there wont be a pure
    `Node` object in the tree

    Parameters
    ----------
    parent : Node
        The `Node` that has this `Node` in its `children` list
    children : list
        A list of `Node`s that are below this `Node` in the tree
    position : tuple
        A 3 length tuple with the line number, column number 
        and filename describing where this `Node` is located in
        the source code
    '''

    _IS_SCOPE = True
    _IS_PARENT = True

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        self.children = kwargs.pop('children', None) or list()
        self.children.extend(args)
        self.position = kwargs.pop('position', None)
        self._scope = dict()

    def pprint_list(self, include_self=True) -> list:
        '''
        Return a Pretty-Printable list of the tree structure

        Parameters
        ----------
        include_self : bool
            Whether or not to include self in the returned list.
            Defaults to `True`

        Returns
        -------
        list
            A list of all children and their children etc.
        '''

        l = [self] if include_self else list()
        for child in self.children:
            l.append(child)
            cpl = child.pprint_list(False)
            if cpl:
                l.append(cpl)
        return l

    def add_child(self, child) -> None:
        '''
        Add `child` to `Node.children`
        
        Parameters
        ----------
        child : Node
            The new child to add as a `Node`
        '''

        self.children.append(child)

    def isleaf(self) -> bool:
        '''
        A `Node` is a leaf if it has no children

        Returns
        -------
        bool
            `True` if the `Node` is a leaf, `False` otherwise
        '''
 
        return not len(self.children)

    def scope_set(self, _id:str, value):
        '''
        Change the value of `_id` in the current scope
        
        Parameters
        ----------
        _id : str
            The identity of the scope item as a string
        value
            The new value for the `_id`

        Returns
        -------
        value
            The value passed in the `value` parameter
        '''

        return self._update_scope(_id, value)

    def scope_get(self, _id:str, orig=None):
        '''
        Retrieve `_id` from the current scope
        
        Parameters
        ----------
        _id : str
            The identity of the scope item as a string
        orig : Optional
            Use this if the origin of the `scope_get` call is not `self`

        Returns
        -------
        value
            The value of `_id` in the current scope

        Raises
        ------
        PyllowNameError
            if `_id` is not defined
        '''

        orig = orig or self
        if self._IS_SCOPE and _id in self._scope:
            return self._scope[_id]
        elif self.parent:
            return self.parent.scope_get(_id, orig)
        raise PyllowNameError(f'Name "{_id}" is not defined', orig.position)

    def _update_scope(self, _id:str, value):
        '''
        Checks if this should update its scope and then updates it.
        This is necessary because not all Nodes should store a scope (e.g. a loop)

        Parameters
        ----------
        _id : str
            The identity of the scope item as a string
        value
            The new value for the `_id`

        Returns
        -------
        value
            The value passed in the `value` parameter
        '''

        if self._IS_SCOPE:
            self._scope[_id] = value
            return value
        return self.parent._update_scope(_id, value)

    def _set_parents(self) -> None:
        '''
        Sets the correct parent for all nodes in the tree
        '''

        for child in self.children:
            self._set_self_as_parent(child)
            child._set_parents()

    def _set_self_as_parent(self, node) -> None:
        '''
        Set the parent of `node` depending on `_IS_PARENT`
        '''

        if self._IS_PARENT:
            node.parent = self
        else:
            self.parent._set_self_as_parent(node)

    def process(self):
        '''
        Raises `NotImplementedError`
        It is supposed to be overwritten when subclassing
        '''

        raise NotImplementedError()

    def __repr__(self):
        return f'<{self.__class__.__name__}: len(children)={len(self.children)}>'

    def __eq__(self, other):
        '''
        Only tests equality in structure, not in value
        '''

        return self.__class__ == other.__class__ and \
            len(self.children) == len(other.children) and \
            all(x == y for x, y in \
            zip(self.children, other.children))

    def __ne__(self, other):
        return not self.__eq__(other)

    
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


class BlockNode(TopNode):
    '''The first node in a sub-tree'''

    _IS_SCOPE = False
    _IS_PARENT = False


class Expression(Node):
    '''Expression class for expressions'''

    _IS_SCOPE = False

    pass


class Statement(Node):
    '''Statement class for statements'''

    pass


class BinaryExpression(Expression):
    '''
    BinaryExpression class for binary expressions
    lhs and rhs will be the first and second children
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left = self.children[0]
        self.right = self.children[1]

    @classmethod
    def make(cls, lhs, op, rhs, *args, **kwargs):
        '''
        Decide what subclass belongs to the `op` symbol
        and return an that object instantiated with 
        `lhs`, `rhs`, `args` and `kwargs`  

        Parameters
        ----------
        lhs
            The left hand operator
        op
            The operator symbol
        rhs
            The right hand operator

        Returns
        -------
        BinaryExpression
            Or rather a subclass thereof based on `op`

        Raises
        ------
        KeyError
            If there is no subclass associated with `op`
        '''

        return {
            CD.PLUS:AdditionExpression,
            CD.MINUS:SubtractionExpression,
            CD.ASTERISK:MultiplicationExpression,
            CD.DIVISION:DivisionExpression,
            CD.POWER:PowerExpression,
            CD.EQ:EqualExpression,
            CD.NE:NotEqualExpression,
            CD.AND:AndExpression,
            CD.OR:OrExpression,
            CD.NOT:NotExpression,
            CD.GT:GreaterThanExpression,
            CD.LT:LessThanExpression,
            CD.GE:GreaterThanEqualExpression,
            CD.LE:LessThanEqualExpression
        }[op](lhs, rhs, *args, **kwargs)

    def _op(self, lhs, rhs):
        raise NotImplementedError()

    def process(self):
        self.left = self.left.process()
        self.right = self.right.process()
        return self._op(self.left, self.right)

    def __repr__(self):
        return f'<{self.__class__.__name__}: left="{self.left.__class__.__name__}", right="{self.right.__class__.__name__}">'


def exprify(token) -> Expression:
    '''
    Make a `MonoExpression` from a `Token`

    Parameters
    ----------
    token
        This is either a `Token` or an `Expression`

    Returns
    -------
    MonoExpression
        made from the `token` parameter

    Raises
    ------
    PyllowSyntaxError
        If the token.type is not `MonoExpression`able
    '''

    if not isinstance(token, Expression):
        return MonoExpression.make(token)
    return token


class MonoExpression(Expression):
    '''
    For leaf expression nodes like numbers and identities

    Parameters
    ----------
    value : str
        The value of the `MonoExpression`, be it a number or identifier
    tokentype : str
        The type of the token, could be 'num', 'bool', etc
    subtype : str
        The `Token._subtype`, only necessary when `tokentype` is not
        specific enough, e.g. 'num' could be either 'int' or 'float'

    Raises
    ------
    PyllowSyntaxError
        If there is no `MonoExpression` associated with `tokentype`
    '''

    ALLOWED_TYPES = ('bool', 'int', 'float', 'str', 'id')

    def __init__(self, value, tokentype=None, subtype=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.children = list()
        self.type = subtype or tokentype
        if self.type not in self.ALLOWED_TYPES:
            raise PyllowSyntaxError('Invalid syntax', self.position)

    @classmethod
    def make(cls, token, *args, **kwargs) -> Expression:
        '''
        Make a MonoExpression from a `Token` object instead of
        passing the parameters manually

        Parameters
        ----------
        token : Token
            A `Token` to extract relevant information from which 
            makes generating a `MonoExpression` much easier

        Returns
        -------
        MonoExpression
            Instantiated from the `Token` passed in the `token`
            parameter

        Raises
        ------
        PyllowSyntaxError
            If there is no `MonoExpression` associated with `token.type`
        '''

        return MonoExpression(
            value=token.value,
            tokentype=token.type,
            subtype=token._subtype,
            position=token.position,
            *args, **kwargs 
        )

    def process(self):
        '''
        Return the relevant datatype for this `MonoExpression`
        '''

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
    '''AdditionExpression for additive expressions'''

    def _op(self, lhs, rhs):
        return lhs + rhs


class SubtractionExpression(BinaryExpression):
    '''SubtractionExpression for subtractive expressions'''

    def _op(self, lhs, rhs):
        return lhs - rhs


class MultiplicationExpression(BinaryExpression):
    '''MultiplicationExpression for multiplicative expressions'''

    def _op(self, lhs, rhs):
        return lhs * rhs


class DivisionExpression(BinaryExpression):
    '''DivisionExpression for divisive expressions'''

    def _op(self, lhs, rhs):
        return lhs / rhs


class PowerExpression(BinaryExpression):
    '''PowerExpression for power expressions'''

    def _op(self, lhs, rhs):
        return lhs ** rhs


class EqualExpression(BinaryExpression):
    '''EqualExpression for equality expressions'''

    def _op(self, lhs, rhs):
        return lhs == rhs


class NotEqualExpression(BinaryExpression):
    '''NotEqualExpression for non-equality expressions'''

    def _op(self, lhs, rhs):
        return lhs != rhs


class AndExpression(BinaryExpression):
    '''AndExpression for and expressions'''

    def _op(self, lhs, rhs):
        return lhs and rhs


class OrExpression(BinaryExpression):
    '''OrExpression for or expressions'''

    def _op(self, lhs, rhs):
        return lhs or rhs


class GreaterThanExpression(BinaryExpression):
    '''GreaterThanExpression for greater-than expressions'''

    def _op(self, lhs, rhs):
        return lhs > rhs


class LessThanExpression(BinaryExpression):
    '''LessThanExpression for less-than expressions'''

    def _op(self, lhs, rhs):
        return lhs < rhs


class GreaterThanEqualExpression(BinaryExpression):
    '''GreaterThanEqualExpression for greater-than-equal expressions'''

    def _op(self, lhs, rhs):
        return lhs >= rhs


class LessThanEqualExpression(BinaryExpression):
    '''LessThanEqualExpression for less-than-equal expressions'''

    def _op(self, lhs, rhs):
        return lhs <= rhs


class UnaryExpression(Expression):
    '''
    For unary expressions
    
    Parameters
    ----------
    value
        Value of the unary expression before it has been processed
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = kwargs.pop('value', None) or self.children[0]

    def _op(self, value):
        raise NotImplementedError()

    def process(self):
        self.value = self.value.process()
        return self._op(self.value)

    @classmethod
    def make(cls, op, *args, **kwargs):
        '''
        Return one of the `UnaryExpression` subclasses based on `op`

        Parameters
        ----------
        op : str
            The operator symbol as a string

        Returns
        -------
        UnaryExpression
            Based on `op`

        Raises
        ------
        KeyError
            if `op` has no associated `UnaryExpression`
        '''

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
    '''
    For variable assignment
    
    Parameters
    ----------
    identity : str
        The identity of the variable
    '''

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
    '''
    For if/else if/else statements

    Parameters
    ----------
    condition : Expression
        An expression that when evaluated determines
        if `self.block` is processed 
    block : BlockNode
        A BlockNode with the contents of the if statement
    alt : IfStatement, BlockNode
        If the condition evalutes to a falsy value, this
        IfStatement/BlockNode will be processed
    '''

    _IS_SCOPE = False

    def __init__(self, condition, block, alt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.condition = condition
        self.block = block
        self.alt = alt
        if self.alt:
            self.alt.parent = self
        self.block.parent = self
        self.condition.parent = self
        self.condition._set_parents()

    def process(self):
        self.condition = self.condition.process()
        if self.condition:
            self.block.process()
        elif self.alt:
            self.alt.process()

    def __repr__(self):
        return f'<{self.__class__.__name__}: condition="{self.condition}", len(block)={len(self.block.children)}, bool(alt)={bool(self.alt)}>'
        