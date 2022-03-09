""" Test module. Auto pytest that can be started in IDE or with::

    python -m pytest

in terminal in tests folder.
"""
from . import test_cicd
from . import test_helpers

__all__ = ["test_cicd", "test_helpers"]
