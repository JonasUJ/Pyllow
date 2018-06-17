'''Datatype base class'''


from .chardef import CD
from .Error import PyllowTypeError, PyllowValueError, PyllowZeroDivisionError


class Datatype:
    '''Datatype base class'''

    DATATYPE = NotImplemented

    def __init__(self, value, position):
        self.value = value
        self.position = position

    def _typeerror(self, other, op):
        raise PyllowTypeError(f'Unsupported operation "{op}" on types: "{other.DATATYPE}" and "{self.DATATYPE}"', self.position)

    def _add_(self, other):
        return self.value + other

    def _sub_(self, other):
        return self.value - other

    def _mul_(self, other):
        return self.value * other

    def _div_(self, other):
        return self.value / other

    def _pow_(self, other):
        return self.value ** other

    def _bool_(self):
        return bool(self.value)

    def _neg_(self):
        return - self.value

    def _pos_(self):
        return + self.value

    def _abs_(self):
        return abs(self.value)

    def _not_(self):
        return not self.value

    def __repr__(self):
        return f'<{self.__class__.__name__}: value={self.value}>'

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)


class Float(Datatype):
    '''Float datatype'''

    DATATYPE = 'float'
    DEFAULT_VALUE = 0.0

    def __init__(self, value, position):
        super().__init__(value, position)
        try:
            self.value = float(self.value or self.DEFAULT_VALUE)
        except ValueError:
            raise PyllowValueError(f'Cannot convert "{self.value}" to {self.DATATYPE}', self.position)

    def __add__(self, other):
        try:
            if isinstance(self, other.__class__):
                return other.__class__(self._add_(other.value), self.position)
            return self.__class__(self._add_(other.value), self.position)
        except TypeError:
            self._typeerror(other, CD.PLUS)

    def __sub__(self, other):
        try:
            if isinstance(self, other.__class__):
                return other.__class__(self._sub_(other.value), self.position)
            return self.__class__(self._sub_(other.value), self.position)
        except TypeError:
            self._typeerror(other, CD.MINUS)
        
    def __mul__(self, other):
        try:
            if isinstance(self, other.__class__):
                return other.__class__(self._mul_(other.value), self.position)
            return self.__class__(self._mul_(other.value), self.position)
        except TypeError:
            self._typeerror(other, CD.ASTERISK)
        
    def __truediv__(self, other):
        try:
            return Float(self._div_(other.value), self.position)
        except TypeError:
            self._typeerror(other, CD.DIVISION)
        except ZeroDivisionError:
            raise PyllowZeroDivisionError('Division by zero', self.position)
        
    def __pow__(self, other):
        try:
            if isinstance(self, other.__class__):
                other.__class__(self._pow_(other.value), self.position)
            return self.__class__(self._pow_(other.value), self.position)
        except TypeError:
            self._typeerror(other, CD.POWER)

    # Weird name becasue __bool__ must return True/False
    def _fBool(self):
        return Bool(self._bool_(), self.position)

    def __neg__(self):
        return self.__class__(self._neg_(), self.position)

    def __pos__(self):
        return self.__class__(self._pos_(), self.position)

    def __abs__(self):
        return self.__class__(self._abs_(), self.position)
    
    def __not__(self):
        return Bool(self._not_(), self.position)


class Integer(Float):
    '''Integer datatype'''

    DATATYPE = 'int'
    DEFAULT_VALUE = 0

    def __init__(self, value, position):
        super().__init__(value, position)
        try:
            self.value = int(self.value or self.DEFAULT_VALUE)
        except ValueError:
            raise PyllowValueError(f'Cannot convert "{self.value}" to {self.DATATYPE}', self.position)


class Bool(Integer):
    '''Bool datatype'''

    DATATYPE = 'bool'

    def __init__(self, value, *args, **kwargs):

        if value == CD.TRUE:
            value = 1
        elif value == CD.FALSE:
            value = 0

        super().__init__(value, *args, **kwargs)

        if self.value:
            self.value = 1
        else:
            self.value = 0
