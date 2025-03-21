from . import ast, object_
from .builtins_ import builtins

def new_error(msg):
    return object_.Error(msg)


NULL = object_.Null()
TRUE = object_.Boolean(True)
FALSE = object_.Boolean(False)

def eval_(node: ast.Node, env: object_.Environment) -> object_.Object:
    if isinstance(node, ast.Program):
        return evaluate_program(node, env)

    if isinstance(node, ast.ExpressionStatement):
        return eval_(node.Expression_, env)

    if isinstance(node, ast.IntegerLiteral):
        return object_.Integer(node.Value)

    if isinstance(node, ast.StringLiteral):
        return object_.String(node.Value)

    if isinstance(node, ast.Boolean):
        return TRUE if node.Value else FALSE

    if isinstance(node, ast.PrefixExpression):
        right = eval_(node.Right, env)
        if isinstance(right, object_.Error): return right
        return evaluate_prefix_expression(node.Operator, right)

    if isinstance(node, ast.InfixExpression):
        left = eval_(node.Left, env)
        if isinstance(left, object_.Error): return left
        right = eval_(node.Right, env)
        if isinstance(right, object_.Error): return right
        return evaluate_infix_expression(node.Operator, left, right)

    if isinstance(node, ast.IFExpression):
        cond = eval_(node.Condition, env)
        if isinstance(cond, object_.Error): return cond
        return eval_(node.Consequence, env) if cond.Value else eval_(node.Alternative, env)

    if isinstance(node, ast.BlockStatement):
        return evaluate_block_statements(node, env)

    if isinstance(node, ast.ReturnStatement):
        res = eval_(node.Value, env)
        if isinstance(res, object_.Error): return res
        return object_.ReturnValue(res)

    if isinstance(node, ast.LetStatement):
        val = eval_(node.Value, env)
        env.set_(node.Name.Value, val)
        return NULL

    if isinstance(node, ast.Identifier):
        val = env.get(node.Value)
        if val is not None: return val
        val = builtins.get(node.Value, None)
        if val is not None: return val
        return new_error(f'identifier not found: {node.Value}')

    if isinstance(node, ast.FunctionLiteral):
        return object_.Function(Params=node.Parameters, Body=node.Body, env=env)

    if isinstance(node, ast.CallExpression):
        func = eval_(node.Function, env)
        if isinstance(func, object_.Error): return func
        args = evaluate_expressions(node.Arguments, env)
        if len(args) == 1 and isinstance(args[0], object_.Error): return args[0]
        return apply_function(func, args)

    if isinstance(node, ast.ArrayLiteral):
        Elements = evaluate_expressions(node.Elements, env)
        if len(Elements) == 1 and isinstance(Elements[0], object_.Error): return Elements[0]
        return object_.Array(Elements)

    if isinstance(node, ast.IndexExpression):
        return evaluate_index_expression(node, env)

    if isinstance(node, ast.HashLiteral):
        Elements = evaluate_pairs(node.Elements, env)
        if isinstance(Elements, object_.Error): return Elements
        return object_.Hash(Elements=Elements)


    return NULL

def evaluate_program(node: ast.Node, env: object_.Environment) -> object_.Object:
    ret = NULL
    for stmt in node.Statements:
        ret = eval_(stmt, env)
        if isinstance(ret, object_.ReturnValue):
            return ret.Value
        elif isinstance(ret, object_.Error):
            return ret
    return ret

def evaluate_block_statements(node: ast.Node, env: object_.Environment) -> object_.Object:
    ret = NULL
    for stmt in node.Statements:
        ret = eval_(stmt, env)
        if isinstance(ret, object_.ReturnValue) or isinstance(ret, object_.Error):
            return ret
    return ret


def evaluate_prefix_expression(operator, right) -> object_.Object:
    if operator == '!': return evaluate_bang_operator_expression(right)
    if operator == '-': return evaluate_minus_prefix_operator_expression(right)


def evaluate_bang_operator_expression(right: object_.Object) -> object_.Object:
    if isinstance(right, object_.Null):
        return TRUE

    if isinstance(right, object_.Boolean):
        return FALSE if right.Value else TRUE

    if isinstance(right, object_.Integer):
        return TRUE if right.Value == 0 else FALSE

    return FALSE

def evaluate_minus_prefix_operator_expression(right: object_.Object) -> object_.Object:
    if isinstance(right, object_.Integer):
        return object_.Integer(-right.Value)

    return new_error(f'unknown operator: -{right.Type()}')

def evaluate_infix_expression(operator: str, left: object_.Object, right: object_.Object) -> object_.Object:
    if left.Type() != right.Type(): return new_error(f'type mismatch: {left.Type()} {operator} {right.Type()}')

    if left.Type() == object_.INTEGER_OBJ: return evaluate_integer_infix_expression(operator, left, right)
    if left.Type() == object_.BOOLEAN_OBJ: return evaluate_boolean_infix_expression(operator, left, right)
    if left.Type() == object_.STRING_OBJ: return evaluate_string_infix_expression(operator, left, right)

    if not (
        (isinstance(left, object_.Integer) or isinstance(left, object_.Boolean)) and
        (isinstance(right, object_.Integer) or isinstance(right, object_.Boolean))
        
    ): return new_error(f'unknown operator: {left.Type()} {operator} {right.Type()}')

def evaluate_integer_infix_expression(operator, left, right):
    if operator == '==': return TRUE if left.Value == right.Value else FALSE
    if operator == '!=': return TRUE if left.Value != right.Value else FALSE

    if operator == '+': return object_.Integer(left.Value + right.Value)
    if operator == '-': return object_.Integer(left.Value - right.Value)
    if operator == '*': return object_.Integer(left.Value * right.Value)
    if operator == '/':
        if right.Value != 0: return new_error(f"division by zero")
        return object_.Integer(left.Value // right.Value)

    if operator == '<': return TRUE if left.Value < right.Value else FALSE
    if operator == '>': return TRUE if left.Value > right.Value else FALSE

    return new_error(f"unknown operator: {left.Type()} {operator} {right.Type()}")

def evaluate_boolean_infix_expression(operator, left, right):
    if operator == '==': return TRUE if left.Value == right.Value else FALSE
    if operator == '!=': return TRUE if left.Value != right.Value else FALSE
    return new_error(f"unknown operator: {left.Type()} {operator} {right.Type()}")

def evaluate_string_infix_expression(operator, left, right):
    if operator == '+': return object_.String(left.Value + right.Value)
    return new_error(f"unknown operator: {left.Type()} {operator} {right.Type()}")



def evaluate_expressions(nodes: list[ast.Node], env: object_.Environment) -> list[object_.Object]:
    results: list[object_.Object] = []
    for node in nodes:
        res = eval_(node, env)
        if isinstance(res, object_.Error): return [res]
        results.append(res)
    return results

def apply_function(func: object_.Object, args: list[object_.Object]) -> object_.Object:
    if isinstance(func, object_.Function):
        new_env = object_.Environment(func.env)
        if len(func.Params) != len(args): return new_error(f'len of args dont match len of parameters: {len(args)} != {len(func.Params)}')
        for p, a in zip(func.Params, args): new_env.set_(p.Value, a)
        evaluated = eval_(func.Body, new_env)
        if isinstance(evaluated, object_.ReturnValue): evaluated = evaluated.Value
        return evaluated

    elif isinstance(func, object_.BuiltIn): return func.func(args)

    return new_error(f"not a function: {func.Type()}")

def evaluate_index_expression(node, env):
    left = eval_(node.Left, env)
    if isinstance(left, object_.Error): return left
    if left.Type() not in (object_.ARRAY_OBJ, object_.HASH_OBJ): return new_error(f'left is not array or hash, got {left.Type()}')

    right = eval_(node.Right, env)
    if isinstance(right, object_.Error): return right
    if left.Type() == object_.ARRAY_OBJ:
        if not isinstance(right, object_.Integer): return new_error(f'right is not integer, got {right.Type()}')
        if right.Value >= len(left.Elements): return new_error(f'array index {right.Value} out of range for array of len {len(left.Elements)}')
        if right.Value < 0: return new_error(f'we do not support negative indexing; got {right.Value}')
        return left.Elements[right.Value]

    elif left.Type() == object_.HASH_OBJ:
        if right.Type() not in (object_.STRING_OBJ, object_.BOOLEAN_OBJ, object_.INTEGER_OBJ):
            return new_error(f'key type should be one of STRING, BOOLEAN or INTEGER. got={right.Type()}')

        if right not in left.Elements.keys():
            return new_error(f'key not found')
        return left.Elements[right]

def evaluate_pairs(Elements, env):
    result = {}
    for node in Elements:
        Key = eval_(node[0], env)
        if Key.Type() not in (object_.STRING_OBJ, object_.BOOLEAN_OBJ, object_.INTEGER_OBJ):
            return new_error(f'key type should be one of STRING, BOOLEAN or INTEGER. got={Key.Type()}')
        Value = eval_(node[1], env)
        result[Key] = Value

    return result
