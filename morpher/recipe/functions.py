from typing import Callable, Any

_registered_functions: dict[str, Callable[[Any], Any]] = {}

def register_function(name: str, f: Callable[[Any], Any]):
    """Register function `f` to be used in recipes under the `name` 

    Args:
        name (str): name of the function
        f (Callable[[Any], Any]): function
    """
    _registered_functions[name] = f

def registered_functions() -> dict[str, Callable[[Any], Any]]:
    """Returns the dictionary with all registered functions

    Returns:
        dict[str, Callable[[Any], Any]]: dictionary with names of the functions as keys and functions as values
    """
    return _registered_functions
