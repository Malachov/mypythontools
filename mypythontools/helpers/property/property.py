"""Module with functions for 'property' subpackage."""

from __future__ import annotations

from typing import Generic, TypeVar, Callable, Type, overload, Any

from typeguard import check_type

from .. import type_hints


T = TypeVar("T")
U = TypeVar("U")


# Needs to inherit from property to be able to use help tooltip
class MyPropertyClass(property, Generic[T]):
    """Python property on steroids. Check module docstrings for more info."""

    # Property is inherited just for formatting help in IDE, so not called from init
    def __init__(self, fget: Callable[..., T] = None, doc=None):  # pylint: disable=super-init-not-called

        if fget:
            self.allowed_types = type_hints.get_return_type_hints(fget)

            self.init_function = fget

            if doc:
                self.__doc__ = doc
            elif fget.__doc__:
                self.__doc__ = fget.__doc__
            else:
                self.__doc__ = None

        self.public_name = ""
        self.private_name = ""

    def default_fset(self, used_object, content) -> None:
        """Define how new values will be stored."""
        setattr(used_object, self.private_name, content)

    def __set_name__(self, _, name):
        self.public_name = name
        self.private_name = "_" + name

    @overload
    def __get__(self, used_object: None, objtype: Any = None) -> MyPropertyClass[T]:
        ...

    @overload
    def __get__(self, used_object: U, objtype: Type[U] = None) -> T:
        ...

    def __get__(self, used_object, objtype=None):
        if not used_object:
            return self

        # Expected value can be nominal value or function, that return that value
        content = getattr(used_object, self.private_name)
        if callable(content):
            if not content.__code__.co_varnames:
                value = content()
            else:
                value = content(used_object)
        else:
            value = content

        return value

    def __set__(self, used_object, content: T | Callable[..., T]):

        # You can setup value or function, that return that value
        if callable(content):
            result = content(used_object)
        else:
            result = content

        if self.allowed_types:
            check_type(expected_type=self.allowed_types, value=result, argname=self.public_name)

        self.default_fset(used_object, result)


# Define as static method as it can be used directly
def init_my_properties(self):
    """Property usually get value of some private variable. This remove the necessity of declaring it as
    it us initialized automatically."""
    if not hasattr(self, "myproperties_list"):
        setattr(self, "myproperties_list", [])

    for i in vars(type(self)).values():
        if isinstance(i, MyPropertyClass):
            self.myproperties_list.append(i.public_name)
            setattr(
                self,
                i.private_name,
                i.init_function,
            )


def MyProperty(f: Callable[..., T]) -> MyPropertyClass[T]:  # pylint: disable=invalid-name
    """If not using this workaround, but use class decorator, IDE complains that property has no defined
    setter. On the other hand, it use correct type hint."""
    return MyPropertyClass[T](f)


# TODO - Use PEP 614 and define type just i n class decorator
# Python 3.9 necessary

# if __name__ == "__main__":

#     from typing_extensions import Literal

#     class Example:
#         def __init__(self) -> None:
#             init_my_properties(self)

#         @MyProperty
#         def var_literal(self) -> Literal["One", "Two"]:  # Literal options are also validated
#             return "One"

#     a = Example.var_literal
#     example = Example()

#     a = example.var_literal  # In VS Code help str instead of Literal

#     example.var_literal = "One"  # Correct
#     example.var_literal = "Six"  # This should not work
#     example.var_literal = 1  # If int, it's correct

#     def with_function() -> Literal["efe"]:
#         return "efe"

#     example.var_literal = with_function  # This is the same ... () -> str instead of str () -> Literal[]
