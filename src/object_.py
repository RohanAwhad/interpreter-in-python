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

