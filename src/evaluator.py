from . import ast, object_

NULL = object_.Null()
TRUE = object_.Boolean(True)
FALSE = object_.Boolean(False)

def eval_(node: ast.Node) -> object_.Object:
    if isinstance(node, ast.Program):
        return evaluate_statements(node)

    if isinstance(node, ast.ExpressionStatement):
        return eval_(node.Expression_)

    if isinstance(node, ast.IntegerLiteral):
        return object_.Integer(node.Value)

    if isinstance(node, ast.Boolean):
        return TRUE if node.Value else FALSE

    if isinstance(node, ast.PrefixExpression):
        right = eval_(node.Right)
        return evaluate_prefix_expression(node.Operator, right)

    if isinstance(node, ast.InfixExpression):
        left = eval_(node.Left)
        right = eval_(node.Right)
        return evaluate_infix_expression(node.Operator, left, right)

    if isinstance(node, ast.IFExpression):
        cond = eval_(node.Condition)
        return eval_(node.Consequence) if cond.Value else eval_(node.Alternative)

    if isinstance(node, ast.BlockStatement):
        return evaluate_statements(node)


    return NULL

def evaluate_statements(node: ast.Node) -> object_.Object:
    ret = NULL
    for stmt in node.Statements:
        ret = eval_(stmt)
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

    return NULL

def evaluate_infix_expression(operator: str, left: object_.Object, right: object_.Object) -> object_.Object:
    if not (
        (isinstance(left, object_.Integer) or isinstance(left, object_.Boolean)) and
        (isinstance(right, object_.Integer) or isinstance(right, object_.Boolean))
        
    ): return NULL

    if operator == '==': return TRUE if left.Value == right.Value else FALSE
    if operator == '!=': return TRUE if left.Value != right.Value else FALSE
    if isinstance(left, object_.Boolean) or isinstance(right, object_.Boolean): return NULL
    # booleans as operands are only supported for '==' and '!=' operators

    if operator == '+': return object_.Integer(left.Value + right.Value)
    if operator == '-': return object_.Integer(left.Value - right.Value)
    if operator == '*': return object_.Integer(left.Value * right.Value)
    if operator == '/':
        assert (right.Value != 0) and (right.Value != False), f"Division by Zero Error"
        return object_.Integer(left.Value // right.Value)

    if operator == '<': return TRUE if left.Value < right.Value else FALSE
    if operator == '>': return TRUE if left.Value > right.Value else FALSE

