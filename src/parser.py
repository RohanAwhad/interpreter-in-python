from typing import Callable
from pydantic import BaseModel
from enum import IntEnum, auto

from . import ast, lexer, token

class Precedence(IntEnum):
  _ = auto()
  LOWEST = auto()
  EQUALS = auto()  # ==
  LESSGREATER = auto()  # > or <
  SUM = auto()  # + or -
  PRODUCT = auto()  # * or /
  PREFIX = auto()  # -X or !X
  CALL = auto()  # myFunction(X)

precedence_map = {
    token.EQ      : Precedence.EQUALS,
    token.NOT_EQ  : Precedence.EQUALS,
    token.PLUS    : Precedence.SUM,
    token.MINUS   : Precedence.SUM,
    token.ASTERISK: Precedence.PRODUCT,
    token.SLASH   : Precedence.PRODUCT,
    token.LT      : Precedence.LESSGREATER,
    token.GT      : Precedence.LESSGREATER,
}

class Parser(BaseModel):
    l: lexer.Lexer

    curr_token: token.Token | None = None
    peek_token: token.Token | None = None
    errors    : list[str] | None = None

    prefix_parse_fns: dict[token.TokenType, Callable] | None = None
    infix_parse_fns : dict[token.TokenType, Callable] | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_token()
        self.next_token()

        self.errors = []

        self.prefix_parse_fns = {}
        self.register_prefix_parse_fns(token.IDENT, self.parse_identifier)
        self.register_prefix_parse_fns(token.INT, self.parse_integer_literal)
        self.register_prefix_parse_fns(token.MINUS, self.parse_prefix_expression)
        self.register_prefix_parse_fns(token.BANG, self.parse_prefix_expression)
        self.register_prefix_parse_fns(token.TRUE, self.parse_boolean)
        self.register_prefix_parse_fns(token.FALSE, self.parse_boolean)
        self.register_prefix_parse_fns(token.LPARAN, self.parse_grouped_expression)

        self.infix_parse_fns = {}
        self.register_infix_parse_fns(token.EQ      , self.parse_infix_expression)
        self.register_infix_parse_fns(token.NOT_EQ  , self.parse_infix_expression)
        self.register_infix_parse_fns(token.PLUS    , self.parse_infix_expression)
        self.register_infix_parse_fns(token.MINUS   , self.parse_infix_expression)
        self.register_infix_parse_fns(token.ASTERISK, self.parse_infix_expression)
        self.register_infix_parse_fns(token.SLASH   , self.parse_infix_expression)
        self.register_infix_parse_fns(token.LT      , self.parse_infix_expression)
        self.register_infix_parse_fns(token.GT      , self.parse_infix_expression)

    def register_prefix_parse_fns(self, token_type: token.TokenType, fn: Callable) -> None:
        self.prefix_parse_fns[token_type] = fn

    def register_infix_parse_fns(self, token_type: token.TokenType, fn: Callable) -> None:
        self.infix_parse_fns[token_type] = fn
        

    def next_token(self):
        self.curr_token = self.peek_token
        self.peek_token = lexer.next_token(self.l)


    def parse_program(self) -> ast.Program | None:
        program = ast.Program(Statements=[])

        while not self.is_curr_token_type(token.EOF):
            try:
                statement = self.parse_statement()
                if statement is not None:
                    program.Statements.append(statement)
            except Exception as e:
                self.errors.append(str(e))
            finally:
                self.next_token()
        return program

    def parse_statement(self) -> ast.Statement | None:
        if self.is_curr_token_type(token.LET):
            return self.parse_let_statement()
        if self.is_curr_token_type(token.RETURN):
            return self.parse_return_statement()

        return self.parse_expression_statement()

    def parse_return_statement(self) -> ast.ReturnStatement | None:
        Token = self.curr_token
        while not self.is_curr_token_type(token.SEMICOLON):
            self.next_token()
        return ast.ReturnStatement(Token=Token)

    def parse_let_statement(self) -> ast.LetStatement | None:
        Token = self.curr_token

        self.expect_peek(token.IDENT)
        Name = self._new_identifier(self.curr_token, self.curr_token.literal)

        self.expect_peek(token.ASSIGN)
        while not self.is_curr_token_type(token.SEMICOLON):
            self.next_token()

        return ast.LetStatement(Token=Token, Name=Name, Expression=None)

    def is_curr_token_type(self, token_type) -> bool:
        return self.curr_token.type_ == token_type

    def is_peek_token_type(self, token_type) -> bool:
        return self.peek_token.type_ == token_type

    def expect_peek(self, token_type) -> bool:
        assert self.is_peek_token_type(token_type), f'Parsing error. Expected Token Type = "{token_type}", but got "{self.peek_token.type_}"'

        self.next_token()
        return True
        
    def _new_identifier(self, Token: token.Token, Value: str) -> ast.Identifier:
        return ast.Identifier(Token=Token, Value=Value)

    def parse_expression_statement(self) -> ast.ExpressionStatement | None:
        Token = self.curr_token
        exprsn = self.parse_expression(Precedence.LOWEST)
        if self.is_peek_token_type(token.SEMICOLON):
            self.next_token()
        return ast.ExpressionStatement(Token=Token, Expression_=exprsn)

    def parse_expression(self, precedence: Precedence):
        assert self.curr_token.type_ in self.prefix_parse_fns, f"no prefix parse function found for '{self.curr_token.type_}'"
        prefix_fn = self.prefix_parse_fns[self.curr_token.type_]
        left_expression = prefix_fn();

        while (not self.is_peek_token_type(token.SEMICOLON)) \
            and (precedence < self.peek_precedence()):
            assert self.peek_token.type_ in self.infix_parse_fns, f"no infix parse function found for '{self.peek_token.type_}'"
            infix_fn = self.infix_parse_fns[self.peek_token.type_]
            self.next_token()
            left_expression = infix_fn(left_expression)

        return left_expression


    def parse_identifier(self) -> ast.Expression | None:
        return ast.Identifier(Token=self.curr_token, Value=self.curr_token.literal)

    def parse_integer_literal(self) -> ast.Expression | None:
        return ast.IntegerLiteral(Token=self.curr_token, Value=int(self.curr_token.literal))

    def parse_prefix_expression(self) -> ast.Expression | None:
        Token = self.curr_token
        Operator = self.curr_token.literal
        self.next_token()
        Right = self.parse_expression(Precedence.PREFIX)
        return ast.PrefixExpression(Token=Token, Operator=Operator, Right=Right)

    def peek_precedence(self) -> Precedence:
        return precedence_map.get(self.peek_token.type_, Precedence.LOWEST)

    def curr_precedence(self) -> Precedence:
        return precedence_map.get(self.curr_token.type_, Precedence.LOWEST)

    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression | None:
        expression = ast.InfixExpression(
            Token   =self.curr_token,
            Operator=self.curr_token.literal,
            Left    =left
        )
        precedence = self.curr_precedence()
        self.next_token()
        Right = self.parse_expression(precedence)
        expression.Right = Right
        return expression


    def parse_boolean(self) -> ast.Expression:
        Token = self.curr_token
        Value = self.is_curr_token_type(token.TRUE)
        return ast.Boolean(Token=Token, Value=Value)

    def parse_grouped_expression(self) -> ast.Expression | None:
        self.next_token()
        expression = self.parse_expression(Precedence.LOWEST)
        if self.expect_peek(token.RPARAN):
            return expression
        return None
