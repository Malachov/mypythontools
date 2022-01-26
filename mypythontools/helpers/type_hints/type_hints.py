"""Module with functions for 'type_hints' subpackage."""

from __future__ import annotations
from typing import Any, Callable, Union, Type

from typing_extensions import get_type_hints


def get_return_type_hints(func: Callable) -> Any:
    """Return function return types. This is because `get_type_hints` result in error for some types in older
    versions of python and also that `__annotations__` contains only string, not types.

    Args:
        func (Callable): Function with type hints.

    Returns:
        Any: Type of return.

    Example:
        >>> def union_return() -> int | float:
        ...     return 1
        >>> inferred_type = get_return_type_hints(union_return)
        >>> 'int' in str(inferred_type) and 'float' in str(inferred_type)
        True
        >>> def literal_return() -> Literal[1, 2, 3]:
        ...     return 1
        >>> inferred_type = get_return_type_hints(literal_return)
        >>> 'Literal' in str(inferred_type)
        True
    """
    try:
        types = get_type_hints(func).get("return")
    except Exception:
        types = func.__annotations__.get("return")

    if isinstance(types, str) and "Union" in types:
        types = eval(types, func.__globals__)

    # If Union operator |, e.g. int | str - get_type_hints() result in TypeError
    # Convert it to Union
    elif isinstance(types, str) and "|" in types:
        evaluated_types: Type
        evaluated_types = [eval(i, func.__globals__) for i in types.split("|")]
        types = Union[evaluated_types[0], evaluated_types[1]]

        if len(evaluated_types) > 2:
            for i in evaluated_types[2:]:
                types = Union[types, i]

    return types
