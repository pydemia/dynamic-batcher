import os
import inspect


def validate_string(val):
    if val is None:
        return None
    if not isinstance(val, str):
        raise TypeError("Not a string: %s" % val)
    return val.strip()


def validate_file_exists(val):
    if val is None:
        return None
    if not os.path.exists(val):
        raise ValueError("File %s does not exists." % val)
    return val


def validate_list_string(val):
    if not val:
        return []

    # legacy syntax
    if isinstance(val, str):
        val = [val]

    return [validate_string(v) for v in val]


def validate_list_of_existing_files(val):
    return [validate_file_exists(v) for v in validate_list_string(val)]


def validate_string_to_list(val):
    val = validate_string(val)

    if not val:
        return []

    return [v.strip() for v in val.split(",") if v]


def validate_class(val):
    if inspect.isfunction(val) or inspect.ismethod(val):
        val = val()
    if inspect.isclass(val):
        return val
    return validate_string(val)


def get_arity(f):
    sig = inspect.signature(f)
    arity = 0
    positionals = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    )

    for param in sig.parameters.values():
        if param.kind in positionals:
            arity += 1

    return arity


def validate_callable(arity):
    def _validate_callable(val):
        if isinstance(val, str):
            try:
                mod_name, obj_name = val.rsplit(".", 1)
            except ValueError:
                raise TypeError("Value '%s' is not import string. "
                                "Format: module[.submodules...].object" % val)
            try:
                mod = __import__(mod_name, fromlist=[obj_name])
                val = getattr(mod, obj_name)
            except ImportError as e:
                raise TypeError(str(e))
            except AttributeError:
                raise TypeError("Can not load '%s' from '%s'"
                                "" % (obj_name, mod_name))
        if not callable(val):
            raise TypeError("Value is not callable: %s" % val)
        if arity != -1 and arity != get_arity(val):
            raise TypeError("Value must have an arity of: %s" % arity)
        return val
    return _validate_callable
