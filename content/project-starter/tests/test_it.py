""" Test module. Auto pytest that can be started in IDE or with

    >>> python -m pytest

in terminal in tests folder.
"""
#%%

from pathlib import Path
import os
import inspect
import sys


# Find paths and add to sys.path to be able to import local modules
test_path = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parent
root_path = test_path.parent

if root_path not in sys.path:
    sys.path.insert(0, root_path.as_posix())


import SET_APP__NAME


def test_1():

    assert True
