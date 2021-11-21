"""Module with some helpers for type hints and annotations."""

from __future__ import annotations
from typing import Any, Callable, Union

from typing_extensions import get_type_hints, Literal


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
        ...
        >>> def literal_return() -> Literal[1, 2, 3]:
        ...     return 1
        >>> get_return_type_hints(union_return)
        typing.Union[int, float]
        >>> get_return_type_hints(literal_return)
        typing.Literal[1, 2, 3]

    get_return_type_hints(union_return)
    """
    return_type_str = func.__annotations__.get("return")

    if return_type_str and "Union" in return_type_str:
        types = eval(return_type_str, func.__globals__)

    # If Union operator |, e.g. int | str - get_type_hints() result in TypeError
    # Convert it to Union
    elif return_type_str and "|" in return_type_str:
        evaluated_types = [eval(i, func.__globals__) for i in return_type_str.split("|")]
        types = Union[evaluated_types[0], evaluated_types[1]]

        if len(evaluated_types) > 2:
            for i in evaluated_types[2:]:
                types = Union[types, i]

    else:
        types = get_type_hints(func).get("return")

    return types
