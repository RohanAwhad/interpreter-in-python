from . import object_


def _len_builtin(args: list[object_.Object]) -> object_.Object:
    if len(args) > 1:
        return object_.Error(f'len function takes only 1 argument, but {len(args)} were given')

    s = args[0]
    if s.Type() == object_.STRING_OBJ: return object_.Integer(len(s.Value))
    return object_.Error(f'cannot find len of {s.Type()} type object')


builtins: dict[str, object_.BuiltIn] = {
    'len': object_.BuiltIn(_len_builtin)
}
