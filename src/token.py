from pydantic import BaseModel


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
MINUS = "-"
ASTERISK = "*"
SLASH = "/"

LT = "<"
GT = ">"

BANG = '!'
COMMA = ","
SEMICOLON = ";"

LPARAN = '('
RPARAN = ')'
LBRACE = '{'
RBRACE = '}'

EQ = '=='
NOT_EQ = '!='

FUNCTION = "FUNCTION"
LET = "LET"
TRUE = "TRUE"
FALSE = "FALSE"
IF = "IF"
ELSE = "ELSE"
RETURN = "RETURN"
