from pydantic import BaseModel
from . import ast, lexer, token

class Parser(BaseModel):
    l: lexer.Lexer
    curr_token: token.Token | None = None
    peek_token: token.Token | None = None
    errors: list[str] | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_token()
        self.next_token()
        self.errors = []

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
            except AssertionError as e:
                self.errors.append(str(e))
            finally:
                self.next_token()
        return program

    def parse_statement(self) -> ast.Statement | None:
        if self.is_curr_token_type(token.LET):
            return self.parse_let_statement()

        return None

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

