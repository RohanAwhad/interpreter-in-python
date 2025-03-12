from . import object_
import copy

def _len_builtin(args: list[object_.Object]) -> object_.Object:
    if len(args) > 1:
        return object_.Error(f'len function takes only 1 argument, but {len(args)} were given')
    s = args[0]
    if s.Type() == object_.STRING_OBJ: return object_.Integer(len(s.Value))
    if s.Type() == object_.ARRAY_OBJ: return object_.Integer(len(s.Elements))
    return object_.Error(f'cannot find len of {s.Type()} type object')


def _first_builtin(args: list[object_.Object]) -> object_.Object:
    if len(args) > 1:
        return object_.Error(f'first function takes only 1 argument, but {len(args)} were given')
    s = args[0]
    if s.Type() == object_.ARRAY_OBJ: return s.Elements[0]
    return object_.Error(f'cannot find first of {s.Type()} type object')


def _last_builtin(args: list[object_.Object]) -> object_.Object:
    if len(args) > 1:
        return object_.Error(f'last function takes only 1 argument, but {len(args)} were given')
    s = args[0]
    if s.Type() == object_.ARRAY_OBJ: return s.Elements[-1]
    return object_.Error(f'cannot find last of {s.Type()} type object')


def _rest_builtin(args: list[object_.Object]) -> object_.Object:
    if len(args) > 1:
        return object_.Error(f'rest function takes only 1 argument, but {len(args)} were given')
    s = args[0]
    if s.Type() != object_.ARRAY_OBJ: return object_.Error(f'cannot find rest of {s.Type()} type object')

    new_elements: list[object_.Object] = []
    for elem in s.Elements[1:]:
        new_elements.append(copy.deepcopy(elem))
    return object_.Array(new_elements)


def _push_builtin(args: list[object_.Object]) -> object_.Object:
    if len(args) > 2:
        return object_.Error(f'push function takes only 2 argument, but {len(args)} were given')
    s = args[0]
    if s.Type() != object_.ARRAY_OBJ: return object_.Error(f'cannot push in {s.Type()} type object')

    new_elements: list[object_.Object] = []
    for elem in s.Elements: new_elements.append(copy.deepcopy(elem))
    new_elements.append(args[1])
    return object_.Array(new_elements)


builtins: dict[str, object_.BuiltIn] = {
    'len': object_.BuiltIn(_len_builtin),
    'first': object_.BuiltIn(_first_builtin),
    'last': object_.BuiltIn(_last_builtin),
    'rest': object_.BuiltIn(_rest_builtin),
    'push': object_.BuiltIn(_push_builtin),
}
