from pprint import pprint

from utils import get_parsed_AST_from_raw
from src.Error import PyllowException

# Enable ANSI support in console, thanks stackoverflow
import ctypes
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def print_scope(tree, name=False, **_):
    if not tree: return
    if not name:
        for k, v in tree.tree._scope.items():
            print(f'{k}: {v}')
        return
    try:
        value = tree.tree.scope_get(name)
    except PyllowException:
        print(f'{name} is not defined in global scope')
    else:
        print(f'{name}: {value}')

def print_tree(tree, *_, **__):
    if not tree: return
    pprint(tree.tree.pprint_list())

def print_help(*_, **__):
    for cmd, fn in COMMANDS.items():
        print(f'{cmd}: {fn.__name__}')

INPUT_STR = ' ~ '
COMMAND_STR = '>> '
COMMANDS = {
    'scope': print_scope,
    'tree': print_tree,
    'help': print_help
}

global_scope = {}
total_raw = ''
current_raw = ''
current_tree = False
current_str = COMMAND_STR

while True:
    current_raw = input(current_str)
    if current_raw.startswith('/') and current_str != INPUT_STR:
        clean = current_raw.lstrip('/')
        if len(clean) == 0:
            print('Invalid command')
        command = clean.split(' ')[0]
        if command == clean:
            COMMANDS[command](current_tree)
        else:
            COMMANDS[command](current_tree, *clean.split(' ')[1:])
    elif current_raw == '':
        print(' '*(len(current_raw)+len(INPUT_STR)) + '\033[F' + '\r'*(len(current_raw)+len(INPUT_STR)), end='')
        parsed_AST = get_parsed_AST_from_raw(total_raw)
        parsed_AST.tree._scope = global_scope
        parsed_AST.execute()
        current_tree = parsed_AST
        global_scope = current_tree.tree._scope
        total_raw = ''
        current_str = COMMAND_STR
    else:
        if current_str == COMMAND_STR:
            print(' '*(len(current_raw)+len(COMMAND_STR)) + '\033[F' + '\r'*(len(current_raw)+len(COMMAND_STR)) + INPUT_STR + current_raw, end='\n')
        current_str = INPUT_STR
        total_raw += current_raw + '\n'