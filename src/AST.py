'''Abstract Syntax Tree and Nodes'''

from Stream import Stream
from chardef import CD, PRECEDENCE
from Datatype import *
from Error import *
from Node import *


class TokenStream(Stream):

    pass


class AST:
    '''Abstract Syntax Tree class'''

    def __init__(self, tokens):
        self.tree = TopNode()
        self._stream = TokenStream(tokens)

    def parse(self):
        self._stream.next()
        try:
            while self._statement():
                pass
            if self._stream.is_not_finished:
                error(PyllowSyntaxError('Invalid syntax', self._stream.current.position))
                return False
            return True
        except PyllowException as err:
            error(err)
            return False

    def execute(self):
        try:
            self.tree.process()
            return True
        except PyllowException as err:
            error(err)
            return False

    def _accept(self, *values, attr='type'):

        if getattr(self._stream.current, attr) in values:
            self._stream.next()
            return True
        return False

    def _expect(self, *values, attr='type'):

        if (self._accept(*values, attr)):
            return True

        if attr == 'value':
            raise PyllowSyntaxError(
                f'Invalid syntax, missing {", ".join(values)}',
                self._stream.peek_prev().position
            )

        raise PyllowSyntaxError(
                'Invalid syntax',
                self._stream.peek_prev().position
            )
        
    def _expression(self, nlhs=False, precedence=0):

        def check_syntax():
            if not isinstance(lhs, Expression) and lhs.type not in ('num', 'id', 'bool') or \
                rhs and not isinstance(rhs, Expression) and rhs.type not in ('num', 'id', 'bool'):
                if self._stream.current.type == 'EOF':
                    raise PyllowSyntaxError('Invalid syntax', self._stream.peek_prev().position)
                raise PyllowSyntaxError('Invalid syntax', self._stream.current.position)

        call = self._call()
        if call:
            return call

        rhs = None
        lhs = nlhs or self._stream.next()
        token = self._stream.peek_next()

        if not lhs:
            return False

        elif not isinstance(lhs, Expression):
            if lhs.type == 'LPAREN':
                lhs = self._expression()
                if self._stream.peek_next() and self._stream.peek_next().type == 'RPAREN':
                    self._stream.next()
                    return lhs
                token = self._stream.peek_next()
                
            elif lhs.type == 'EOF':
                self._stream.prev()
                return False

            elif lhs.value in (CD.NOT, CD.PLUS, CD.MINUS):
                if self._stream.peek_prev().type not in ('num', 'RPAREN', 'bool', 'id') and \
                        self._stream.peek_next() and \
                        self._stream.peek_next().type in ('num', 'id', 'bool'):
                    lhs = UnaryExpression.make(
                        lhs.value,
                        exprify(self._stream.peek_next()),
                        position=self._stream.peek_next().position
                    )
                    self._stream.next()
                    token = self._stream.peek_next()

            if self._stream.peek_next().type == 'RPAREN' and \
                    (self._stream.peek_prev().type == 'LPAREN' or \
                    self._stream.peek_prev(2).type == 'LPAREN'):
                self._stream.next()
                return exprify(lhs)

        while token and token.type == 'op' and PRECEDENCE[token.value] >= precedence:
            op = token
            self._stream.next()

            rhs = self._stream.next()
            if rhs.type == 'LPAREN':
                rhs = self._expression()

            elif rhs.value in (CD.NOT, CD.PLUS, CD.MINUS):
                if self._stream.peek_prev().type not in ('num', 'RPAREN', 'bool', 'id') and \
                        self._stream.peek_next() and \
                        self._stream.peek_next().type in ('num', 'id', 'bool'):
                    rhs = UnaryExpression.make(
                        rhs.value,
                        exprify(self._stream.peek_next()),
                        position=self._stream.peek_next().position
                    )
                    self._stream.next()

            if self._stream.peek_next() and self._stream.peek_next().type == 'RPAREN':
                self._stream.next()
                return BinaryExpression.make(
                    exprify(lhs), op.value, exprify(rhs),
                    position=self._stream.current.position)

            token = self._stream.peek_next()
            while token and token.type == 'op' and PRECEDENCE[token.value] > PRECEDENCE[op.value]:
                rhs = self._expression(rhs, PRECEDENCE[token.value])
                token = self._stream.peek_next()
                if self._stream.current.type == 'RPAREN':
                    token = None
                    break

            lhs = BinaryExpression.make(
                exprify(lhs), op.value, exprify(rhs), 
                position=self._stream.current.position)

        check_syntax()

        if not isinstance(lhs, Expression):
            lhs = exprify(lhs)

        return lhs

    def _assignment(self):
        
        _id = self._stream.current.value
        if self._accept('id'):
            if self._accept('assign'):
                value = self._expression(self._stream.current)
                self._stream.next()
                return AssignStatement(_id, value, position=self._stream.current.position)
            self._stream.prev()
        return False

    def _statement(self):

        assign = self._assignment()
        if assign:
            self.tree.add_child(assign)
            return True

        elif self._accept(('num', 'id', 'bool', 'op')):
            self.tree.add_child(self._expression())
            return True

        elif self._accept(CD.IF, attr='value'):
            self.tree.add_child(self._if())
            return True

        elif self._expression():
            return True

        #self._stream.next()
        return False

    def _call(self):

        if self._accept('id'):
            if self._accept('LPAREN'):
                identity = self._stream.prev(2)

                self._expect('id', 'num')
                args = list(self._stream.prev())

                while not self._accept('sep'):
                    arg = self._expression()
                    if not arg:
                        self._expect('id', 'num')
                    args.append(arg if arg else self._stream.prev())

                self._expect('RPAREN')

                return CallExpression(identity, *args, position=self._stream.current.position)
            self._stream.prev()
        return False

    def _if(self):
        cond = self._expression()
        if not cond:
            raise PyllowSyntaxError('Invalid syntax: missing condition',
                self._stream.peek_prev().position
            )
        self._expect(CD.BLOCKSTART, attr='value')
        while self._statement():
            pass
        self._expect(CD.BLOCKEND, attr='value')
