"""This is not module that configure library mypythontools, but module that help create config for your project.

What
====

1) Simple and short syntax.
2) Ability to have docstrings on variables (not dynamically, so visible in IDE) and good for sphinx docs.
3) Type checking and Literal checking via MyProperty.
4) Also function evaluation from other config values (not only static value stored).
5) Options hierarchy (nested options).

Examples:
=========

    >>> from typing_extensions import Literal
    ...
    >>> class SimpleConfig(ConfigBase):
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
    >>> config = SimpleConfig()
    >>> config.var
    123
    >>> config.var = 665
    >>> config.var
    665
    >>> config['var']  # You can also access params as in a dictionary
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

This is how help looks like in VS Code

.. image:: /_static/intellisense.png
    :width: 620
    :alt: tasks
    :align: center


Hierarchical config
-------------------

If last level, do inherit from ConfigBase, else inherit from ConfigStructured

Note:
    Use unique values for all config variables even if they are in various subconfig.

>>> class Config(ConfigStructured):
...     def __init__(self) -> None:
...         self.subconfig1 = self.SubConfiguration1()
...         self.subconfig2 = self.SubConfiguration2()
...
...     class SubConfiguration1(ConfigStructured):
...         def __init__(self) -> None:
...             self.subsubconfig = self.SubSubConfiguration()
...
...         class SubSubConfiguration(ConfigBase):
...             @MyProperty
...             def value1() -> Literal[0, 1, 2, 3]:
...                 '''Documentation here
...
...                 Options: [0, 1, 2, 3]
...                 '''
...                 return 3
...
...             @MyProperty
...             def value2(self):
...                 return self.value1 + 1
...
...     class SubConfiguration2(ConfigBase):
...         @MyProperty
...         def other_val(self):
...             return self.value2 + 1
...
...     # Also subconfig category can contain values itself
...     @MyProperty
...     def value3() -> int:
...         return 3
...
>>> config = Config()
...
>>> config.subconfig1.subsubconfig.value2
4

You can access value from config as well as from subcategory

>>> config.value2
4

Copy
----

Sometimes you need more instances of settings and you need copy of existing configuration. Copy is deepcopy by default.

>>> config2 = config.copy()
>>> config2.value3 = 0
>>> config2.value3
0
>>> config.value3
3

Bulk update
-----------

Sometimes you want to update many values with flat dictionary.

>>> config.update({'value3': 2, 'value1': 0})
>>> config.value3
2
>>> config.update({"not_existing": "Should fail"})
Traceback (most recent call last):
AttributeError: ...

Get flat dictionary
-------------------

There is a function that will export all the values to the flat dictionary (no dynamic anymore, just values).

>>> config.get_dict()
{'value3': 2, 'value1': 0, 'value2': 1, 'other_val': 2}

Reset
-----
You can reset to default values

>>> config.value1 = 1
>>> config.reset()
>>> config.value1
3

CLI
---
CLI is provided by argparse. When using `with_argparse` method, it will

1) Create parser and add all arguments with help
2) Parse users' sys args and update config

::

    config.with_argparse()

Now you can use in terminal like.

::

    python my_file.py --value1 12


Only basic types like int, float, str, list, dict, set are possible as eval for using type like numpy
array or pandas dataframe could be security leak.

Sphinx docs
===========

If you want to have documentation via sphinx, you can add this to conf.py::

    napoleon_custom_sections = [
        ("Types", "returns_style"),
        ("Type", "returns_style"),
        ("Options", "returns_style"),
        ("Default", "returns_style"),
        ("Example", "returns_style"),
        ("Examples", "returns_style"),
    ]

Here is example

.. image:: /_static/config_on_sphinx.png
    :width: 620
    :alt: tasks
    :align: center
"""

from __future__ import annotations
from typing import Any, TypeVar
from copy import deepcopy
import argparse
import sys

import mylogging

from .property import MyProperty, init_my_properties
from . import misc


# TODO - check if some arg name not more times - would be overwritten


ConfigType = TypeVar("ConfigType", bound="ConfigBase")


class ConfigMeta(type):
    """Metaclass that will edit Config class. Main reason is for being able to define own __init__ but
    still has functionality from parent __init__ that is necessary. With this meta, there is no need
    to use super().__init__ by user.

    As user, you probably will not need it. It's used internally if inheriting from ConfigStructured."""

    def __init__(cls, name, bases, dct) -> None:

        # Avoid base classes here and wrap only user class init
        if name not in [
            "ConfigBase",
            "ConfigStructured",
        ]:

            def add_parent__init__(
                self, dict_values=None, frozen=None, *a, **kw,
            ):

                self._base_config_map = {}
                self.myproperties_list = []
                self.properties_list = []
                self._is_inherited = True

                # Call user defined init
                cls._original__init__(self, *a, **kw)

                init_my_properties(self)

                for i, j in vars(type(self)).items():
                    if type(j) is property:
                        self.properties_list.append(i)

                # If structured config, add proxies to subconfigs
                if self._is_structured:
                    self._propagate_base_config_map()

                # Update values from dict param in init
                if dict_values:
                    for i, j in dict_values.items():
                        setattr(self, i, j)

                if frozen is None:
                    self.frozen = True
                else:
                    self.frozen = frozen

            cls._original__init__ = cls.__init__
            cls.__init__ = add_parent__init__

    def __getitem__(self, key):
        return getattr(self, key)


class ConfigBase(metaclass=ConfigMeta):
    """Main config class. If need nested config, use ConfigStructured instead.
    You can find working examples in module docstrings."""

    # Usually this config is created from someone else that user using this config. Therefore new attributes
    # should not be created. It is possible to force it (raise error). It is possible to set frozen to False
    # to enable creating new instances.
    frozen = False

    _is_inherited = False
    _is_structured = False

    # _base_config_map is used only if using structured config. You can access attribute from subconfig as
    # well as from main config object, there is proxy mapping config dict (same for base and subconfig) if
    # attribute not found on defined object, it will find if it's in this dict where are all config values as
    # key and config object where it's stored. It's poppulated automatically in metaclass during init
    _base_config_map = {}

    def __init__(self, *args, **kwargs) -> None:
        """Init is wrapped in metaclass so __init__ can be overridden by user

        Note:
            You don't need to use parameters from wrapper in your init (but you can use it on instance).
        Args in wrapper:
            dict_values (dict, optional): Values that will updated after init. Defaults to None.
            frozen (bool, optional): If frozen, it's not possible to add new attributes. Defaults to None.
        """
        if not self._is_inherited:
            raise TypeError(
                mylogging.return_str(
                    "Class is not supposed to be called. Just inherit it to create custom config class."
                )
            )

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __getattr__(self, name: str):
        try:
            # If structured config. Value may not be in this object, but in another related object.
            return getattr(self._base_config_map[name], name)

        except KeyError:

            if name not in [
                "_pytestfixturefunction",
                "__wrapped__",
                "pytest_mock_example_attribute_that_shouldnt_exist",
                "__bases__",
                "__test__",
            ]:

                raise AttributeError(mylogging.return_str(f"Variable {name} not found in config."))

    def __setattr__(self, name: str, value: Any) -> None:
        setter_name = name[1:] if name.startswith("_") else name

        if (
            not self.frozen
            or name == "frozen"
            or name in [*self.myproperties_list, *self.properties_list, *vars(self),]
        ):
            object.__setattr__(self, name, value)

        elif setter_name in self._base_config_map.keys():
            setattr(
                self._base_config_map[setter_name], name, value,
            )

        else:
            raise AttributeError(
                mylogging.return_str(
                    f"Object {str(self)} is frozen. New attributes cannot be set and attribute < {name} > not found. Maybe you misspelled name. "
                    "If you really need to change the value, set attribute frozen to false."
                )
            )

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __call__(self, *args: Any, **kwds) -> None:
        raise TypeError(
            mylogging.return_str(
                "Class is not supposed to be called. Just inherit it to create custom config."
            )
        )

    def copy(self: ConfigType) -> ConfigType:
        """Create deep copy of config and all it's attributes.

        Returns:
            ConfigType: Deep copy.
        """
        return deepcopy(self)

    def update(self, dict: dict) -> None:
        """Bulk update with dict values.

        Args:
            dict (dict): E.g {"arg_1": "value"}

        Raises:
            AttributeError: If some arg not found in config.
        """
        for i, j in dict.items():
            if hasattr(self, i):
                setattr(self, i, j)
            else:
                raise AttributeError(mylogging.return_str(f"Config has no attribute {i}"))

    def reset(self) -> None:
        """Reset config to it's default values."""
        copy = type(self)()

        for i in vars(copy).keys():
            setattr(self, i, copy[i])

        for i in copy.myproperties_list:
            setattr(self, i, copy[i])

        for i in copy.properties_list:
            setattr(self, i, copy[i])

    def get_dict(self) -> dict:
        """Get flat dictionary with it's values"

        Returns:
            dict: Flat config dict.
        """
        normal_vars = {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("__")
            and not callable(value)
            and not hasattr(value, "myproperties_list")
            and key
            not in ["myproperties_list", "properties_list", "frozen", "_base_config_map", "_is_inherited"]
        }

        property_vars = {
            # Values from myproperties
            **{key: getattr(self, key) for key in self.myproperties_list},
            # Values from properties
            **{key: getattr(self, key) for key in self.properties_list},
        }

        normal_vars = {
            i: j for i, j in normal_vars.items() if not (i.startswith("_") and i[1:] in property_vars)
        }

        return {**normal_vars, **property_vars}

    def with_argparse(self, about: str | None = None) -> None:
        """
        For using with CLI. When using `with_argparse` method, it will

        1) Create parser and add all arguments with help
        2) Parse users' sys args and update config

        ::

            config.with_argparse()

        Now you can use in terminal like.

        ::

            python my_file.py --config_arg config_value

        Only basic types like int, float, str, list, dict, set are possible as eval for using type like numpy
        array or pandas dataframe could be security leak."""
        if len(sys.argv) > 1 and not misc.GLOBAL_VARS.JUPYTER:

            # Add settings from command line if used
            parser = argparse.ArgumentParser(usage=about)

            config_dict = self.get_dict()

            for i in config_dict.keys():
                try:
                    help = type(self)[i].__doc__
                except AttributeError:
                    help = type(self._base_config_map[i])[i].__doc__

                parser.add_argument(f"--{i}", help=help)

            parsed_args = parser.parse_known_args()

            if parsed_args[1]:
                raise RuntimeError(
                    mylogging.return_str(f"Sys arg parse failed on unknown args: {parsed_args[1]}")
                )

            # Non empty command line args
            parser_args_dict = {}

            # All variables are parsed as strings
            # If it should not be string, infer type
            for i, j in parsed_args[0].__dict__.items():

                if j is None:
                    continue

                if self._is_structured:
                    used_type = type(self._base_config_map[i])[i].allowed_types
                else:
                    used_type = type(self)[i].allowed_types

                if used_type is not str:
                    parser_args_dict[i] = misc.str_to_infer_type(j)
                else:
                    parser_args_dict[i] = j

            self.update(parser_args_dict)


class ConfigStructured(ConfigBase):
    """Class for creating config. Read why and how in config module docstrings."""

    _is_structured = True

    def __init__(self, dict_values=None, frozen=None) -> None:
        """Init is redefined in metaclass so __init__ can be overridden by user

        Args:
            dict_values (dict, optional): Values that will updated after init. Defaults to None.
            frozen (bool, optional): If frozen, it's not possible to add new attributes. Defaults to None.
        """
        super().__init__()
        pass

    def get_dict(self) -> dict:
        # From main class
        dict_of_values = super().get_dict()
        # From sub configs
        for i in vars(self).values():
            if hasattr(i, "myproperties_list"):
                subconfig_dict = i.get_dict()
                dict_of_values.update(subconfig_dict)

        return dict_of_values

    def _propagate_base_config_map(self) -> None:

        for i in vars(self).values():
            if hasattr(i, "myproperties_list"):
                for j in i.myproperties_list:
                    self._base_config_map[j] = i

            elif hasattr(i, "properties_list"):
                for j in i.properties_list:
                    self._base_config_map[j] = i

            if isinstance(i, ConfigBase):
                i._base_config_map = self._base_config_map

            if ConfigStructured in type(i).mro():
                i._propagate_base_config_map()
