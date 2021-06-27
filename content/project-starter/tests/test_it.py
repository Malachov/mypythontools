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
ROOT_PATH = test_path.parent

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH.as_posix())


import SET_APP__NAME


def test_1():

    assert True
