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

    def __str__(self):
        return '\n'.join([str(s) for s in self.Statements])


class Identifier(Expression, BaseModel):
    Token: token.Token  # IDENT Token
    Value: str

    class Config:
        arbitrary_types_allowed = True

    def token_literal(self) -> str: return self.Token.literal

    def __str__(self):
        return self.Value

class IntegerLiteral(Expression, BaseModel):
    Token: token.Token  # INT Token
    Value: int

    class Config:
        arbitrary_types_allowed = True

    def token_literal(self) -> str: return self.Token.literal

    def __str__(self):
        return str(self.Value)

class Boolean(Expression, BaseModel):
    Token: token.Token
    Value: bool

    class Config: arbitrary_types_allowed=True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return str(self.Token.literal)


class PrefixExpression(Expression, BaseModel):
    Token: token.Token
    Operator: str
    Right: Expression | None = None

    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return f'({self.Operator}{self.Right})'

class InfixExpression(Expression, BaseModel):
    Token: token.Token  # could PLUS, MINUS, ASTERISK ...
    Operator: str
    Left: Expression | None = None
    Right: Expression | None = None

    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return f'({self.Left} {self.Operator} {self.Right})'

class LetStatement(Statement, BaseModel):
    Token: token.Token  # LET Token
    Name: Identifier
    Value: Expression | None = None  # TODO: for the timebeing, will remove this soon

    class Config:
        arbitrary_types_allowed = True

    def token_literal(self) -> str: return self.Token.literal

    def __str__(self) -> str:
        return f"{self.Token.literal} {self.Name} = {self.Value if self.Value is not None else ''};"


class ReturnStatement(Statement, BaseModel):
    Token: token.Token  # RETURN Token
    Value: Expression | None = None  # TODO: will not be none in the future

    class Config:
        arbitrary_types_allowed = True

    def token_literal(self) -> str: return self.Token.literal

    def __str__(self):
        return f"{self.Token.literal} {self.Value if self.Value is not None else ''};"

class ExpressionStatement(Statement, BaseModel):
    Token: token.Token  # what will this token be?
    Expression_: Expression | None = None

    class Config:
        arbitrary_types_allowed = True

    def token_literal(self) -> str: return self.Token.literal

    def __str__(self):
        return str(self.Expression_) if self.Expression_ is not None else ''

class BlockStatement(Statement, BaseModel):
    Token: token.Token
    Statements: list[Statement]

    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return '\n'.join([str(x) for x in self.Statements])


class IFExpression(Expression, BaseModel):
    Token: token.Token
    Condition: Expression
    Consequence: BlockStatement
    Alternative: BlockStatement | None = None

    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self) -> str:
        ret = f"IF {self.Condition} {self.Consequence}"
        if self.Alternative is not None:
            ret += f" else {self.Alternative};"
        return ret


class FunctionLiteral(Expression, BaseModel):
    Token: token.Token
    Parameters: list[Identifier];
    Body: BlockStatement

    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self):
        return f"FN ({', '.join([str(x) for x in self.Parameters])}) {self.Body}"


class CallExpression(Expression, BaseModel):
    Token: token.Token
    Function: Expression
    Arguments: list[Expression]

    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return f"{self.Function} ({', '.join([str(x) for x in self.Arguments])})"

class StringLiteral(Expression, BaseModel):
    Token: token.Token
    Value: str
    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return '"'+self.Value+'"'


class ArrayLiteral(Expression, BaseModel):
    Token: token.Token
    Elements: list[Expression]
    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return f"[{', '.join([str(x) for x in self.Elements])}]"

class IndexExpression(Expression, BaseModel):
    Token: token.Token
    Left: Expression
    Right: Expression
    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return f"{self.Left}[{self.Right}]"

class HashLiteral(Expression, BaseModel):
    Token: token.Token
    Elements: list[tuple[Expression, Expression]]
    class Config: arbitrary_types_allowed = True
    def token_literal(self) -> str: return self.Token.literal
    def __str__(self): return '{' + ', '.join([f'{x}: {y}' for x, y in self.Elements]) + ' }'
