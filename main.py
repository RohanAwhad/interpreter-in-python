from pydantic import BaseModel, field_validator


TokenType = str

class Token(BaseModel):
    type_: TokenType
    literal: str | None


# ===
# Token Types
# ===

ILLEGAL = "ILLEGAL"
EOF = "EOF"

IDENT = "IDENT"
INT = "INT"

ASSIGN = "="
PLUS = "+"

COMMA = ","
SEMICOLON = ";"

LPARAN = '('
RPARAN = ')'
LBRACE = '{'
RBRACE = '}'

FUNCTION = "FUNCTION"
LET = "LET"

# ===
# Reading source code
# ===

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
    '=': ASSIGN,
    '+': PLUS,
    ',': COMMA,
    ';': SEMICOLON,
    '(': LPARAN,
    ')': RPARAN,
    '{': LBRACE,
    '}': RBRACE,
}
KEYWORDS_DICT = {
    'let': LET,
    'fn': FUNCTION,
}

def new_token(tt: TokenType, ch: str | None) -> Token: return Token(type_=tt, literal=ch)

def is_letter(ch: str | None) -> bool:
    if ch is None: return False
    return ch.isalpha()

def read_identifier(l: Lexer):
    pos = l.pos
    while is_letter(l.ch):
        read_char(l)
    return l.inp[pos: l.pos]

def lookup_ident(ident: str) -> TokenType:
    if ident in KEYWORDS_DICT: return KEYWORDS_DICT[ident]
    return IDENT

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

def next_token(l: Lexer) -> Token:
    skip_whitespace(l)

    if l.ch in SPECIAL_CHARS_DICT:
        tok = new_token(SPECIAL_CHARS_DICT[l.ch], l.ch)
        read_char(l)  # NOTE: this placement is different from in the book
        return tok

    if is_letter(l.ch):
        ident = read_identifier(l)
        tt = lookup_ident(ident)
        return new_token(tt, ident)
    if is_number(l.ch):
        num = read_num(l)
        tt = INT
        return new_token(tt, num)

    if l.ch is None:
        tok = new_token(EOF, '')
        return tok

    tok = new_token(ILLEGAL, l.ch)
    read_char(l)
    return tok


# ===
# Test Lexer
# ===

if __name__ == '__main__':
    inp = """let five = 5;
let ten = 10;

let add = fn(x, y) {
    x+y;
}

let result = add(five, ten);
"""

    l = Lexer(inp=inp)
    read_char(l)
    cnt = 0
    while True:
        tok = next_token(l)
        print(tok)
        if tok.type_ == EOF:
            break
        # if cnt > 5: break
        # cnt += 1
