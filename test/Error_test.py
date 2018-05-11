import unittest
from src.Error import error, PyllowException


ERROR = PyllowException(position=(1, 3, 'test/Error_test.plw'), errormsg='test error')
ERROR_MSG = '''
test/Error_test.plw
PyllowException occurred on line 1
test
   ^
test error
'''


class ErrorTest(unittest.TestCase):

    def test_error(self):
        self.assertMultiLineEqual(error(ERROR, prints=False), ERROR_MSG)

if __name__ == '__main__':
    unittest.main()
