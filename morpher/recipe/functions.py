from typing import Callable, Any

_registered_functions: dict[str, Callable[[Any], Any]] = {}

def register_function(name: str, f: Callable[[Any], Any]):
    _registered_functions[name] = f

def registered_functions() -> dict[str, Callable[[Any], Any]]:
    return _registered_functions
