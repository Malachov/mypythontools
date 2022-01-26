"""
Module with miscellaneous functions that do not fit into other subpackage but are not big enough have it's own
subpackage. You can find here for example 'json_to_py' that can convert json string to correct python types or
'str_to_infer_type' that will convert string to correct type.
"""

from mypythontools.helpers.misc.misc import (
    check_library_is_available,
    check_type,
    DEFAULT_TABLE_FORMAT,
    get_console_str_with_quotes,
    GLOBAL_VARS,
    json_to_py,
    small_validate,
    str_to_bool,
    str_to_infer_type,
    TimeTable,
    validate,
    watchdog,
)

__all__ = [
    "check_library_is_available",
    "check_type",
    "DEFAULT_TABLE_FORMAT",
    "get_console_str_with_quotes",
    "GLOBAL_VARS",
    "json_to_py",
    "small_validate",
    "str_to_bool",
    "str_to_infer_type",
    "TimeTable",
    "validate",
    "watchdog",
]
