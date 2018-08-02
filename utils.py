from typing import List

from src.AST import AST
from src.Lexer import Lexer, Token


def get_tokens_from_raw(raw:str) -> List[Token]:
    '''
    Get a list of tokens from raw text

    Parameters
    ----------
    raw : str
        raw text
    
    Returns
    -------
    list[Token]
        A list of all tokens found in `raw`

    Raises
    ------
    PyllowException if something like a syntax error is present in `raw`
    '''

    lexer = Lexer()
    return lexer.lex(raw)

def get_AST_from_raw(raw:str) -> AST:
    '''
    Get an AST from raw text

    Parameters
    ----------
    raw : str
        raw text

    Returns
    -------
    An unparsed AST object
    
    Raises
    ------
    PyllowException if something like a syntax error is present in `raw`
    '''

    return AST(get_tokens_from_raw(raw))

def get_parsed_AST_from_raw(raw:str) -> AST:
    '''
    Get a TopNode from raw text

    Parameters
    ----------
    raw : str
        raw text

    Returns
    -------
    A parsed AST object, use `get_parsed_AST_from_raw(raw).tree` to get a TopNode
    
    Raises
    ------
    PyllowException if something like a syntax error is present in `raw`
    '''

    tree = get_AST_from_raw(raw)
    tree.parse()
    return tree

def execute_from_raw(raw:str) -> None:
    '''
    Execute Pyllow code from raw text

    Parameters
    ----------
    raw : str
        raw text

    Returns
    -------
    None
    
    Raises
    ------
    PyllowException if something like a syntax error is present in `raw`
    '''

    get_parsed_AST_from_raw(raw).execute()