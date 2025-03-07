from abc import abstractmethod, ABC
from pydantic import BaseModel
from . import token


class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str: pass

class Statement(Node, ABC):
    def statement_node(self) -> None: pass

class Expression(Node, ABC):
    def expression_node(self) -> None: pass

# ===

class Program(Node, BaseModel):
    Statements: list[Statement]

    class Config:
        arbitrary_types_allowed = True
    
    def token_literal(self):
        if len(self.Statements) > 0: return self.Statements[0].token_literal()
        return ""


class Identifier(Expression, BaseModel):
    Token: token.Token  # IDENT Token
    Value: str

    class Config:
        arbitrary_types_allowed = True

    def token_literal(self) -> str: return self.Token.literal


class LetStatement(Statement, BaseModel):
    Token: token.Token  # LET Token
    Name: Identifier
    Value: Expression | None = None  # TODO: for the timebeing, will remove this soon

    class Config:
        arbitrary_types_allowed = True

    def token_literal(self) -> str: return self.Token.literal

