from . import ast, object_

NULL = object_.Null()
TRUE = object_.Boolean(True)
FALSE = object_.Boolean(False)

def eval_(node: ast.Node) -> object_.Object:
    if isinstance(node, ast.Program):
        return evaluate_program(node)

    if isinstance(node, ast.ExpressionStatement):
        return eval_(node.Expression_)

    if isinstance(node, ast.IntegerLiteral):
        return object_.Integer(node.Value)

    if isinstance(node, ast.Boolean):
        return TRUE if node.Value else FALSE

    if isinstance(node, ast.PrefixExpression):
        right = eval_(node.Right)
        if isinstance(right, object_.Error): return right
        return evaluate_prefix_expression(node.Operator, right)

    if isinstance(node, ast.InfixExpression):
        left = eval_(node.Left)
        if isinstance(left, object_.Error): return left
        right = eval_(node.Right)
        if isinstance(right, object_.Error): return right
        return evaluate_infix_expression(node.Operator, left, right)

    if isinstance(node, ast.IFExpression):
        cond = eval_(node.Condition)
        if isinstance(cond, object_.Error): return cond
        return eval_(node.Consequence) if cond.Value else eval_(node.Alternative)

    if isinstance(node, ast.BlockStatement):
        return evaluate_block_statements(node)

    if isinstance(node, ast.ReturnStatement):
        res = eval_(node.Value)
        if isinstance(res, object_.Error): return res
        return object_.ReturnValue(res)


    return NULL

def evaluate_program(node: ast.Node) -> object_.Object:
    ret = NULL
    for stmt in node.Statements:
        ret = eval_(stmt)
        if isinstance(ret, object_.ReturnValue):
            return ret.Value
        elif isinstance(ret, object_.Error):
            return ret
    return ret

def evaluate_block_statements(node: ast.Node) -> object_.Object:
    ret = NULL
    for stmt in node.Statements:
        ret = eval_(stmt)
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
    if not (
        (isinstance(left, object_.Integer) or isinstance(left, object_.Boolean)) and
        (isinstance(right, object_.Integer) or isinstance(right, object_.Boolean))
        
    ): return new_error(f'unknown operator: {left.Type()} {operator} {right.Type()}')

    if operator == '==': return TRUE if left.Value == right.Value else FALSE
    if operator == '!=': return TRUE if left.Value != right.Value else FALSE
    if isinstance(left, object_.Boolean) or isinstance(right, object_.Boolean): return new_error(f"unknown operator: {left.Type()} {operator} {right.Type()}")
    # booleans as operands are only supported for '==' and '!=' operators

    if operator == '+': return object_.Integer(left.Value + right.Value)
    if operator == '-': return object_.Integer(left.Value - right.Value)
    if operator == '*': return object_.Integer(left.Value * right.Value)
    if operator == '/':
        if right.Value != 0: return new_error(f"division by zero")
        return object_.Integer(left.Value // right.Value)

    if operator == '<': return TRUE if left.Value < right.Value else FALSE
    if operator == '>': return TRUE if left.Value > right.Value else FALSE

def new_error(msg):
    return object_.Error(msg)
