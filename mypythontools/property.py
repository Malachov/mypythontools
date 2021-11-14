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
    >>> config.var = "String is problem"
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.var_literal = 4
    Traceback (most recent call last):
    KeyError: ...
    ...
    >>> config.evaluated
    666
    
    You can still setup a function (or lambda expression) as a new value
    and returned value still will be validated
    >>> config.var = lambda self: self.var_literal + 1

"""

from __future__ import annotations
from typing import Generic, get_type_hints, Union, TypeVar

from typing_extensions import Literal

from .misc import validate

T = TypeVar("T")


class MyPropertyClass(Generic[T]):
    """Python property on steroids. Check module docstrings for more info."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):

        if fget:
            # Validation
            return_type_str = fget.__annotations__.get("return")

            # If Union operator | defined with string - Postponed Evaluation, separate and create normal Union
            # Because get_type_hints() result in TypeError if for example int | str
            if return_type_str and "|" in return_type_str:
                self.types = [eval(i) for i in return_type_str.split("|")]

            else:
                self.types = get_type_hints(fget).get("return")

            # If Union get types for verification
            if hasattr(self.types, "__origin__") and getattr(self.types, "__origin__") == Union:
                self.types = list(self.types.__args__)

            # If Literal - parse options
            elif hasattr(self.types, "__origin__") and getattr(self.types, "__origin__") == Literal:
                self.options = getattr(self.types, "__args__")
                self.types = None
            else:
                self.options = None
            self.init_function = fget

            if fget.__doc__:
                self.__doc__ = self.__doc__

    def default_fset(self, object, content) -> None:
        setattr(object, self.private_name, content)

    def __set_name__(self, _, name):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, object, objtype=None):
        # If getting MyPropertyClass, not object, return MyPropertyClass itself
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

    def __set__(self, object, content):

        # You can setup value or function, that return that value
        if callable(content):
            result = content(object)
        else:
            result = content

        validate(
            result,
            self.types,
            self.options,
            self.public_name,
        )

        # Method defined can be pass as static method
        try:
            self.default_fset(object, content)
        except TypeError:
            self.default_fset(self, object, content)


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


def MyProperty(self):
    """The reason for function workaraund is that it's more clear in IDE help, that
    used attribute is not value, but is result of descriptor __get__ and __set__ functions
    as type in help is not just MyProperty, but () -> USED_TYPE."""
    return MyPropertyClass(self)
