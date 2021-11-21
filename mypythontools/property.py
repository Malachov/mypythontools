"""Module contains MyProperty class that is alternative to normal python property. It's implemented via
descriptor and edited `__get__` and `__set__` magic methods. 

There is default setter, it's possible to auto init values on class init and values in setter can be
validated. This result in much less code written when using a lot of similar properties.

First call is lazy evaluated during first call.

Example of how can it be used is in module config.

Examples:
=========
    >>> from typing_extensions import Literal
    ...
    >>> class Example:
    ...     def __init__(self) -> None:
    ...         init_my_properties(self)
    ...
    ...     @MyProperty
    ...     def var() -> int:  # Type hints are validated.
    ...         '''
    ...         Type:
    ...             int
    ...
    ...         Default:
    ...             123
    ...
    ...         This is docstrings (also visible in IDE, because not defined dynamically).
    ...         Also visible in Sphinx documentation.'''
    ...
    ...         return 123  # This is initial value that can be edited.
    ...
    ...     @MyProperty
    ...     def var_literal(self) -> Literal[1, 2, 3]:  # Literal options are also validated
    ...         return 2
    ...
    ...     @MyProperty
    ...     def evaluated(self) -> int:  # If other defined value is change, computed property is also updated
    ...         return self.var + 1
    ...
    >>> config = Example()
    >>> config.var
    123
    >>> config.var = 665
    >>> config.var
    665
    >>> config.var = "String is problem"  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.var_literal = 4  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.evaluated
    666
    
    You can still setup a function (or lambda expression) as a new value
    and returned value still will be validated
    >>> config.var = lambda self: self.var_literal + 1

"""
from __future__ import annotations

from typing import Generic, TypeVar, Callable

from typeguard import check_type
from typing_extensions import Literal

from . import type_hints


T = TypeVar("T")


class MyPropertyClass(Generic[T]):
    """Python property on steroids. Check module docstrings for more info."""

    def __init__(self, fget: Callable[..., T] = None, fset: Callable = None, fdel=None, doc=None):

        if fget:
            self.allowed_types = type_hints.get_return_type_hints(fget)

            self.init_function = fget

            if fget.__doc__:
                self.__doc__ = self.__doc__

    def default_fset(self, object, content) -> None:
        setattr(object, self.private_name, content)

    def __set_name__(self, _, name):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, object, objtype=None) -> T:
        # If getting MyPropertyClass, not object, return MyPropertyClass itself
        # TODO add @overload with correct types
        if not object:
            return self

        # Expected value can be nominal value or function, that return that value
        content = getattr(object, self.private_name)
        if callable(content):
            if not len(content.__code__.co_varnames):
                value = content()
            else:
                value = content(object)
        else:
            value = content

        return value

    def __set__(self, object, content: T | Callable[..., T]):

        # You can setup value or function, that return that value
        if callable(content):
            result = content(object)
        else:
            result = content

        check_type(expected_type=self.allowed_types, value=result, argname=self.public_name)

        self.default_fset(object, result)


def init_my_properties(self):
    if not hasattr(self, "myproperties_list"):
        setattr(self, "myproperties_list", [])

    for i, j in vars(type(self)).items():
        if type(j) is MyPropertyClass:
            self.myproperties_list.append(j.public_name)
            setattr(
                self,
                j.private_name,
                j.init_function,
            )


def MyProperty(f: Callable[..., T]) -> MyPropertyClass[T]:
    """The reason for function workaraund is that it's more clear in IDE help, that
    used attribute is not value, but is result of descriptor __get__ and __set__ functions
    as type in help is not just MyProperty, but () -> USED_TYPE."""
    return MyPropertyClass[T](f)


# class Example:
#     def __init__(self) -> None:
#         init_my_properties(self)

#     @MyProperty
#     def var_literal(self) -> Literal["asd", "rbrb"]:  # Literal options are also validated
#         return "asd"

# example = Example()

# a = example.var_literal  # In VS Code help str instead of Literal

# example.var_literal = "asd"  # Correct
# example.var_literal = "asdasd"  # This should not work
# example.var_literal = 1  # If int, it's correct


# def withf() -> Literal["efe"]:
#     return "efe"


# example.var_literal = withf  # This is the same ... () -> str instead of str () -> Literal[]
