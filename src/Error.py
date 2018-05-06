'''Errors, Exceptions and such'''


ERROR_MSG = '''
{path}
{error} occurred on line {lineno}
{line}
{col}^
{msg}
'''

def error(err):
    '''Print an error msg formatted to ERROR_MSG from `err`'''

    with open(err.position[2]) as fp:
        line = fp.readlines()[err.position[0]-1].strip('\n')

    print(
        ERROR_MSG.format(
            line=line,
            col=' '*(err.position[1]-1),
            lineno=err.position[0],
            path=err.position[2],
            error=err.__class__.__name__,
            msg=err.errormsg
        )
    )


class PyllowException(Exception):

    def __init__(self, errormsg, position=None):
        self.errormsg = errormsg
        self.position = position


class PyllowValueError(PyllowException):

    pass


class PyllowTypeError(PyllowException):

    pass


class PyllowZeroDivisionError(PyllowException):

    pass


class PyllowSyntaxError(PyllowException):

    pass


class PyllowNameError(PyllowException):

    pass
