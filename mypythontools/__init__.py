"""
mypythontools
=============

Some tools/functions/snippets used across projects.

Usually used from IDE. Root path is infered and things like docs generation on pre-commit
hooks, building application with pyinstaller or deploying to Pypi is matter of calling one function.

Many projects - one codebase.

If you are not sure whether structure of app that will work with this code, there is python starter repo
on `https://github.com/Malachov/my-python-starter`

Paths are infered, but if you have atypical structure or have more projects in cwd, use `mypythontools.misc.set_paths()`.
"""

from . import utils
from . import build
from . import deploy
from . import misc
from . import pyvueel

__version__ = "0.0.24"

__author__ = "Daniel Malachov"
__license__ = "MIT"
__email__ = "malachovd@seznam.cz"

__all__ = ['utils', 'build', 'deploy', 'misc', 'pyvueel']
