import unittest
from src.Lexer import Lexer, RawStream, Token


RAW_TEXT = ''' # comment
id
123
45.6
"string +-*/"
+
-
*
/
^
=
(
)
[
]
{
}
.
|
&
<
>
<=
>=
==
!=
!
if
else
true
false
null'''

TOKENS = (
Token(position=(2, 2, 'test'), type="id", value="id", subtype=None),
Token(position=(3, 2, 'test'), type="num", value="123", subtype="int"),
Token(position=(4, 3, 'test'), type="num", value="45.6", subtype="float"),
Token(position=(5, 12, 'test'), type="str", value="string +-*/", subtype=None),
Token(position=(6, 0, 'test'), type="op", value="+", subtype=None),
Token(position=(7, 0, 'test'), type="op", value="-", subtype=None),
Token(position=(8, 0, 'test'), type="op", value="*", subtype=None),
Token(position=(9, 0, 'test'), type="op", value="/", subtype=None),
Token(position=(10, 0, 'test'), type="op", value="^", subtype=None),
Token(position=(11, 0, 'test'), type="assign", value="=", subtype=None),
Token(position=(12, 0, 'test'), type="LPAREN", value="(", subtype=None),
Token(position=(13, 0, 'test'), type="RPAREN", value=")", subtype=None),
Token(position=(14, 0, 'test'), type="LISTSTART", value="[", subtype=None),
Token(position=(15, 0, 'test'), type="LISTEND", value="]", subtype=None),
Token(position=(16, 0, 'test'), type="BLOCKSTART", value="{", subtype=None),
Token(position=(17, 0, 'test'), type="BLOCKEND", value="}", subtype=None),
Token(position=(18, 0, 'test'), type="op", value=".", subtype=None),
Token(position=(19, 0, 'test'), type="op", value="|", subtype=None),
Token(position=(20, 0, 'test'), type="op", value="&", subtype=None),
Token(position=(21, 0, 'test'), type="op", value="<", subtype=None),
Token(position=(22, 0, 'test'), type="op", value=">", subtype=None),
Token(position=(23, 1, 'test'), type="op", value="<=", subtype=None),
Token(position=(24, 1, 'test'), type="op", value=">=", subtype=None),
Token(position=(25, 1, 'test'), type="op", value="==", subtype=None),
Token(position=(26, 1, 'test'), type="op", value="!=", subtype=None),
Token(position=(27, 0, 'test'), type="op", value="!", subtype=None),
Token(position=(28, 1, 'test'), type="if", value="if", subtype=None),
Token(position=(29, 3, 'test'), type="else", value="else", subtype=None),
Token(position=(30, 3, 'test'), type="bool", value="true", subtype=None),
Token(position=(31, 4, 'test'), type="bool", value="false", subtype=None),
Token(position=(32, 3, 'test'), type="null", value="null", subtype=None),
Token(position=(32, 7, 'test'), type="EOF", value="EOF", subtype=None))


class RawStreamTest(unittest.TestCase):

    def setUp(self):
        self.stream = RawStream(RAW_TEXT, path='test')
        self.stream.next()

    def tearDown(self):
        del self.stream

    def test_lineno(self):
        self.assertEqual(self.stream._lineno, 1)
        self.stream.skip(11)
        self.assertEqual(self.stream._lineno, 2)

    def test_columnno(self):
        self.assertEqual(self.stream._columnno, 0)
        self.stream.skip(8)
        self.assertEqual(self.stream._columnno, 8)
        self.stream.skip(5)
        self.assertEqual(self.stream._columnno, 2)

    def test_next(self):
        self.assertEqual(self.stream.next(), '#')
        self.assertEqual(self.stream._lineno, 1)
        self.assertEqual(self.stream._columnno, 1)
        self.stream.skip(9)
        self.assertEqual(self.stream.next(), 'i')
        self.assertEqual(self.stream._lineno, 2)
        self.assertEqual(self.stream._columnno, 0)
        self.stream._i = len(self.stream._stream) - 1
        self.assertIsNone(self.stream.next())

    def test_prev(self):
        self.stream.skip(12)
        self.assertEqual(self.stream.prev(), 'i')
        self.assertEqual(self.stream._lineno, 2)
        self.assertEqual(self.stream._columnno, 0)
        self.assertEqual(self.stream.prev(), '\n')
        self.assertEqual(self.stream.prev(), 't')
        self.assertEqual(self.stream._lineno, 1)
        self.assertEqual(self.stream._columnno, 9)
        self.stream._i = 0
        self.assertIsNone(self.stream.prev())

    def test_skip(self):
        self.assertEqual(self.stream.skip(1), '#')
        self.assertEqual(self.stream._lineno, 1)
        self.assertEqual(self.stream._columnno, 1)
        self.assertEqual(self.stream.skip(2), 'c')
        self.assertEqual(self.stream._lineno, 1)
        self.assertEqual(self.stream._columnno, 3)
        self.assertEqual(self.stream.skip(8), 'i')
        self.assertEqual(self.stream._lineno, 2)
        self.assertEqual(self.stream._columnno, 0)

    def test_position(self):
        self.assertTupleEqual(self.stream.position(), (1, 0, 'test'))
        self.stream.skip(11)
        self.assertTupleEqual(self.stream.position(), (2, 0, 'test'))
        self.stream.next()
        self.assertTupleEqual(self.stream.position(), (2, 1, 'test'))


class LexerTest(unittest.TestCase):

    def setUp(self):
        self.Lexer = Lexer()
        self.Lexer.lex(RAW_TEXT, path='test')

    def tearDown(self):
        del self.Lexer

    def test_lex(self):
        generated_tokens = tuple(self.Lexer.tokens)
        self.assertTupleEqual(generated_tokens, TOKENS)


class LexFileTest(LexerTest):

    def setUp(self):
        self.Lexer = Lexer()
        self.Lexer.lex_file('test/Lexer_test.plw', error_path='test')

    def test_add_token(self):
        self.Lexer.add_token(position=(1, 0, 'test'), type='id', value='test')
        self.assertEqual(
            self.Lexer.tokens[-1], 
            Token(position=(1, 0, 'test'), type='id', value='test')
        )


if __name__ == '__main__':
    unittest.main()
