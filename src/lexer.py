from pydantic import BaseModel, field_validator
from . import token

class Lexer(BaseModel):
    inp: str
    pos: int = 0
    read_pos: int = 0
    ch: str | None = None  # but has to be of len 1

    @field_validator('ch')
    def check_ch_length(cls, value):
        if value is None: return value
        if len(value) != 1:
            raise ValueError('ch must be a single character')
        return value

def read_char(l: Lexer):
    if l.read_pos >= len(l.inp): l.ch = None
    else: l.ch = l.inp[l.read_pos]
    l.pos = l.read_pos
    l.read_pos += 1

SPECIAL_CHARS_DICT = {
    '=': token.ASSIGN,
    '+': token.PLUS,
    ',': token.COMMA,
    ';': token.SEMICOLON,
    '(': token.LPARAN,
    ')': token.RPARAN,
    '{': token.LBRACE,
    '}': token.RBRACE,
    '[': token.LBRACKET,
    ']': token.RBRACKET,
    '-': token.MINUS,
    '*': token.ASTERISK,
    '/': token.SLASH,
    '<': token.LT,
    '>': token.GT,
    '!': token.BANG,
}
KEYWORDS_DICT = {
    'let': token.LET,
    'fn': token.FUNCTION,
    'true': token.TRUE,
    'false': token.FALSE,
    'if': token.IF,
    'else': token.ELSE,
    'return': token.RETURN,
}

def new_token(tt: token.TokenType, ch: str | None) -> token.Token: return token.Token(type_=tt, literal=ch)

def is_letter(ch: str | None) -> bool:
    if ch is None: return False
    return ch.isalpha()

def read_identifier(l: Lexer):
    pos = l.pos
    while is_letter(l.ch):
        read_char(l)
    return l.inp[pos: l.pos]

def lookup_ident(ident: str) -> token.TokenType:
    if ident in KEYWORDS_DICT: return KEYWORDS_DICT[ident]
    return token.IDENT

def skip_whitespace(l: Lexer):
    IGNORE_CHARS = [' ', '\t', '\n', '\r']
    while l.ch in IGNORE_CHARS: read_char(l)

def is_number(ch: str | None) -> bool:
    if ch is None: return False
    return ch.isdecimal()

def read_num(l: Lexer) -> str:
    pos = l.pos
    while is_number(l.ch):
        read_char(l)
    return l.inp[pos:l.pos]

def next_token(l: Lexer) -> token.Token:
    skip_whitespace(l)

    if l.ch in SPECIAL_CHARS_DICT:
        tok = new_token(SPECIAL_CHARS_DICT[l.ch], l.ch)

        if l.ch == '=':
            read_char(l)
            if l.ch == '=':
                tok = new_token(token.EQ, '==')
                read_char(l)
        elif l.ch == '!':
            read_char(l)
            if l.ch == '=':
                tok = new_token(token.NOT_EQ, '!=')
                read_char(l)
        else:
            read_char(l)  # NOTE: this placement is different from in the book

        return tok


    if is_letter(l.ch):
        ident = read_identifier(l)
        tt = lookup_ident(ident)
        return new_token(tt, ident)
    if is_number(l.ch):
        num = read_num(l)
        tt = token.INT
        return new_token(tt, num)
    if l.ch == '"':
        s = read_string(l)
        if s is None: return new_token(token.ILLEGAL, 'string end not found')
        tt = token.STRING
        return new_token(tt, s)

    if l.ch is None:
        tok = new_token(token.EOF, '')
        return tok

    tok = new_token(token.ILLEGAL, l.ch)
    read_char(l)
    return tok

def read_string(l):
    read_char(l)
    pos = l.pos
    ret = ''
    while l.ch != '"':
        read_char(l)
        if l.ch == '\\':
            ret += l.inp[pos: l.pos]
            read_char(l)
            escape_char = get_escape_char(l.ch)
            ret += escape_char
            read_char(l)
            pos = l.pos

        if l.ch is None:
            return None

    ret += l.inp[pos: l.pos]
    read_char(l)
    return ret

def get_escape_char(ch):
    if ch == 't': return '  '
    if ch == 'n': return '\n'
    return ch
