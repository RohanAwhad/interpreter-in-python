from abc import abstractmethod, ABC
from typing import Callable
from . import ast


class Environment:
    def __init__(self, outer: "Environment" = None):
        self.e: dict[str, Object] = {}
        self.outer = outer

    def get(self, k):
        ret = self.e.get(k, None)
        return self.outer.get(k) if (ret is None and self.outer is not None) else ret

    def set_(self, k, v):
        self.e[k] = v


ObjectType = str

class Object(ABC):
    @abstractmethod
    def Type(self) -> ObjectType: pass

    @abstractmethod
    def Inspect(self) -> str: pass

INTEGER_OBJ  = "INTEGER"
BOOLEAN_OBJ  = "BOOLEAN"
NULL_OBJ     = "NULL"
STRING_OBJ   = "STRING"
RETURN_OBJ   = "RETURN_VALUE"
ERROR_OBJ    = "ERROR"
FUNCTION_OBJ = "FUNCTION"
BUILTIN_OBJ  = "BUILTIN"

class Integer(Object):
    def __init__(self, Value: int): self.Value = Value
    def Type(self): return INTEGER_OBJ
    def Inspect(self) -> str: return str(self.Value)

class Boolean(Object):
    def __init__(self, Value: bool): self.Value = Value
    def Type(self): return BOOLEAN_OBJ
    def Inspect(self): return str(self.Value)

class Null(Object):
    def Type(self): return NULL_OBJ
    def Inspect(self) -> str: return "null"

class String(Object):
    def __init__(self, Value: str): self.Value = Value
    def Type(self): return STRING_OBJ
    def Inspect(self) -> str: return str(self.Value)

class ReturnValue(Object):
    def __init__(self, Value: Object): self.Value = Value
    def Type(self): return RETURN_OBJ
    def Inspect(self): return self.Value.Inspect()

class Error(Object):
    def __init__(self, Message: str): self. Message = Message
    def Type(self): return ERROR_OBJ
    def Inspect(self): return f"Error: {(self.Message)}"

class Function(Object):
    def __init__(self, Params: list[ast.Identifier], Body: ast.BlockStatement, env: Environment):
        self.Params = Params
        self.Body = Body
        self.env = env

    def Type(self) -> ObjectType:
        return FUNCTION_OBJ

    def Inspect(self) -> str:
        ret = f'fn ({", ".join([str(x) for x in self.Params])})' + '{\n' + str(self.Body) + '\n}'
        return ret

class BuiltIn(Object):
    def __init__(self, func: Callable): self.func = func
    def Type(self): return BUILTIN_OBJ
    def Inspect(self): return "builtin function"
