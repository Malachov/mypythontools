"""Module with functions for 'config' subpackage."""


# TODO - check if some arg name not more times - would be overwritten
# TODO - add frozen and dict_values in __init__
# TODO - Remove one loop over vars (from _propagate_base_config_map and do the logic in meta loop)
# TODO - Redefine _base_config_map and properties list on class, not in objects in meta


from __future__ import annotations
from typing import Any, TypeVar
from copy import deepcopy
import argparse
import sys

import mylogging

from ...helpers.property.property import init_my_properties
from ...helpers.misc import misc


ConfigType = TypeVar("ConfigType", bound="ConfigBase")


class ConfigMeta(type):
    """Metaclass that will edit Config class. Main reason is for being able to define own __init__ but
    still has functionality from parent __init__ that is necessary. With this meta, there is no need
    to use super().__init__ by user.

    As user, you probably will not need it. It's used internally if inheriting from ConfigStructured."""

    def __init__(cls, name, bases, dct) -> None:

        type.__init__(cls, name, bases, dct)

        # Avoid base classes here and wrap only user class init
        if name not in [
            "ConfigBase",
            "ConfigStructured",
        ]:

            def add_parent__init__(
                self,
                dict_values=None,
                frozen=None,
                *a,
                **kw,
            ):

                self._base_config_map = {}
                self.myproperties_list = []
                self.properties_list = []

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
            cls.__init__ = add_parent__init__  # type: ignore

    def __getitem__(self, key):
        return getattr(self, key)


class ConfigBase(metaclass=ConfigMeta):  # type: ignore
    """Main config class. If need nested config, use ConfigStructured instead.
    You can find working examples in module docstrings."""

    # Usually this config is created from someone else that user using this config. Therefore new attributes
    # should not be created. It is possible to force it (raise error). It is possible to set frozen to False
    # to enable creating new instances.
    frozen = False

    _is_structured = False

    # _base_config_map is used only if using structured config. You can access attribute from subconfig as
    # well as from main config object, there is proxy mapping config dict (same for base and subconfig) if
    # attribute not found on defined object, it will find if it's in this dict where are all config values as
    # key and config object where it's stored. It's poppulated automatically in metaclass during init
    _base_config_map = {}

    # Can be overwritten by user. Just for linting and type hints
    def __init__(self) -> None:
        self.myproperties_list = []
        self.properties_list = []

    # Just controll that class is subclassed and not instantiated
    def __new__(cls, *args, **kwargs):
        if cls is ConfigBase or cls is ConfigStructured:
            raise TypeError(
                "ConfigBase and ConfigStructured are not supposed to be instantiated" "only to be subclassed."
            )
        return object.__new__(cls, *args, **kwargs)

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

                raise AttributeError(mylogging.format_str(f"Variable {name} not found in config."))

    def __setattr__(self, name: str, value: Any) -> None:
        setter_name = name[1:] if name.startswith("_") else name

        if (
            not self.frozen
            or name == "frozen"
            or name
            in [
                *self.myproperties_list,
                *self.properties_list,
                *vars(self),
            ]
        ):
            object.__setattr__(self, name, value)

        elif setter_name in self._base_config_map:
            setattr(
                self._base_config_map[setter_name],
                name,
                value,
            )

        else:
            raise AttributeError(
                mylogging.format_str(
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
            mylogging.format_str(
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
                raise AttributeError(mylogging.format_str(f"Config has no attribute {i}"))

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
            and key not in ["myproperties_list", "properties_list", "frozen", "_base_config_map"]
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
        array or pandas dataframe could be security leak.

        Args:
            about (str, optional): Description used in --help. Defaults to None.

        Raises:
            RuntimeError: If arg that do not exists in config.

        Note:
            If using boolean, you must specify the value. Just occurrence, e.g. --my_arg is not True."""
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

            try:
                parsed_args = parser.parse_known_args()
            except SystemExit:
                raise RuntimeError(
                    f"Config args parsing failed. Used args {sys.argv}. Check if args and values are correct "
                    "format. Each argument must have just one value. Use double quotes if spaces in string. "
                    "For dict e.g. \"{'key': 666}\". If using bool, there has to be True or False."
                )

            if parsed_args[1]:
                raise RuntimeError(
                    mylogging.format_str(
                        f"Config args parsing failed on unknown args: {parsed_args[1]}."
                        "It may happen if variable not exists in config."
                    )
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
                    try:
                        # May fail if for example Litera["string1", "string2"]
                        parser_args_dict[i] = misc.str_to_infer_type(j)
                    except Exception:
                        parser_args_dict[i] = j
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
                i._propagate_base_config_map()  #  type: ignore
