import unittest
from src.Datatype import Float, Integer, Bool
from src.Error import PyllowTypeError, PyllowZeroDivisionError, PyllowValueError


POSITION = 1, 0, 'test'
LVAL = 5
RVAL = 2

def make(datatype, val):
    return datatype(val, POSITION)


class FloatTest(unittest.TestCase):

    def setUp(self):
        self.datatype = Float
        self.lhs = Float(LVAL, POSITION)
        self.rhs = Float(RVAL, POSITION)

    def test_add(self):
        self.assertEqual(self.lhs + self.rhs, make(self.datatype, LVAL + RVAL))

    def test_sub(self):
        self.assertEqual(self.lhs - self.rhs, make(self.datatype, LVAL - RVAL))

    def test_mul(self):
        self.assertEqual(self.lhs * self.rhs, make(self.datatype, LVAL * RVAL))

    def test_div(self):
        self.assertEqual(self.lhs / self.rhs, make(Float, LVAL / RVAL))

    def test_pow(self):
        self.assertEqual(self.lhs ** self.rhs, make(self.datatype, LVAL ** RVAL))

    def test_fBool(self):
        self.assertEqual(self.lhs._fBool(), make(Bool, bool(LVAL)))

    def test_neg(self):
        self.assertEqual(-self.lhs, make(self.datatype, -LVAL))

    def test_pos(self):
        self.assertEqual(+self.lhs, make(self.datatype, +LVAL))

    def test_abs(self):
        self.assertEqual(abs(self.lhs), make(self.datatype, abs(LVAL)))

    def test_not(self):
        self.assertEqual(self.lhs.__not__(), make(self.datatype, not LVAL))

    def test__typeerror(self):
        with self.assertRaises(PyllowTypeError):
            class other: DATATYPE = 'test'
            self.lhs._typeerror(other(), 'test')

    def test_zero_division(self):
        with self.assertRaises(PyllowZeroDivisionError):
            self.lhs / make(self.datatype, 0.0)

    def test_value_error(self):
        with self.assertRaises(PyllowValueError):
            make(self.datatype, 'test')


class IntegerTest(FloatTest):

    def setUp(self):
        self.datatype = Integer
        self.lhs = Integer(LVAL, POSITION)
        self.rhs = Integer(RVAL, POSITION)


class BoolTest(unittest.TestCase):

    def test_init(self):
        self.assertEqual(make(Bool, LVAL).value, 1)
        self.assertEqual(make(Bool, 0.0).value, 0)
        self.assertEqual(make(Bool, 'true').value, 1)
        self.assertEqual(make(Bool, 'false').value, 0)


if __name__ == '__main__':
    unittest.main()
