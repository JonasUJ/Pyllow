'''Grammar definitions'''

import chardef as cd

def _any(*args):
    def check(other):
        return other in args
    return check
