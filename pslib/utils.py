__all__ = ["compose"]


def compose(*funcs):
    def wrapper(value):
        for func in reversed(funcs):
            value = func(value)
        return value

    return wrapper
