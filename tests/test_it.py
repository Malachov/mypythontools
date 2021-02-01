""" Test module. Auto pytest that can be started in IDE or with

    >>> python -m pytest

in terminal in tests folder.
"""
#%%

import sys
from pathlib import Path
import os
import inspect
import shutil

# Find paths and add to sys.path to be able to import local modules
test_dir_path = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parents[0]
root_path = test_dir_path.parent

if root_path.as_posix() not in sys.path:
    sys.path.insert(0, root_path.as_posix())


def test_it():

    shutil.rmtree(root_path / 'build', ignore_errors=True)
    (root_path / 'docs' / 'source' / 'modules.rst').unlink(missing_ok=True)

    # Git hooks example

    #!/usr/bin/env python
    # -*- coding: UTF-8 -*-

    import mypythontools

    mypythontools.githooks.generate_readme_from_init('mypythontools')
    mypythontools.githooks.sphinx_docs_regenerate('mypythontools')

    # Build app with pyinstaller example

    mypythontools.build.build_app(main_file='app.py', console=True, debug=True)

    assert (root_path / 'build').exists() and (root_path / 'docs' / 'source' / 'modules.rst').exists()
