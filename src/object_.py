from abc import abstractmethod, ABC

ObjectType = str

class Object(ABC):
    @abstractmethod
    def Type(self) -> ObjectType: pass

    @abstractmethod
    def Inspect(self) -> str: pass

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
NULL_OBJ = "NULL"
RETURN_OBJ = "RETURN_VALUE"
ERROR_OBJ = "ERROR"

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

class ReturnValue(Object):
    def __init__(self, Value: Object): self.Value = Value
    def Type(self): return RETURN_OBJ
    def Inspect(self): return self.Value.Inspect()

class Error(Object):
    def __init__(self, Message: str): self. Message = Message
    def Type(self): return ERROR_OBJ
    def Inspect(self): return f"Error: {(self.Message)}"
