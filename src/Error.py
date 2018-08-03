'''Errors, Exceptions and such'''


ERROR_MSG = '''
{path}
{error} occurred on line {lineno}
{line}
{col}^
{msg}
'''

def error(err, prints=True):
    '''Print an error msg formatted to ERROR_MSG from `err`'''

    error_formatted = ERROR_MSG.format(
        line=err.position[3],
        col=' '*(err.position[1]),
        lineno=err.position[0],
        path=err.position[2],
        error=err.__class__.__name__,
        msg=err.errormsg
    )

    if prints: print(error_formatted)
    return error_formatted


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
