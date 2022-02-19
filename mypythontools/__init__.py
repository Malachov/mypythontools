"""
.. image:: https://img.shields.io/pypi/pyversions/mypythontools.svg
    :target: https://pypi.python.org/pypi/mypythontools/
    :alt: Python versions

.. image:: https://badge.fury.io/py/mypythontools.svg
    :target: https://badge.fury.io/py/mypythontools
    :alt: PyPI version

.. image:: https://pepy.tech/badge/mypythontools
    :target: https://pepy.tech/project/mypythontools
    :alt: Downloads

.. image:: https://img.shields.io/lgtm/grade/python/github/Malachov/mypythontools.svg
    :target: https://lgtm.com/projects/g/Malachov/mypythontools/context:python
    :alt: Language grade: Python

.. image:: https://readthedocs.org/projects/mypythontools/badge/?version=latest
    :target: https://mypythontools.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License: MIT

.. image:: https://codecov.io/gh/Malachov/mypythontools/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Malachov/mypythontools
    :alt: Codecov


Some tools/functions/snippets/files used across projects.

It's called mypythontools, but it's also made for you...

Can be used as python library. Things like building the application with pyinstaller, incrementing version,
generating rst files for sphinx docs, pushing to GitHub or deploying to PyPi or other CI/CD functionality,
creating config module or plot data is the matter of calling one function or clicking one button (e.g. Vs Code
task).

Many projects - one codebase.

If you are not sure whether the structure of your app will work with this code, check `project-starter` on
GitHub in content folder.

Paths are inferred, but if you have atypical structure or have more projects in cwd, setup necessary paths in
paths module.

There is also some extra stuff, that is not bundled via PyPI (cookiecutter, CSS for readthedocs etc.), such a
content is under the Content topic.

Links
=====

Official documentation - https://mypythontools.readthedocs.io/

Official repo - https://github.com/Malachov/mypythontools

Installation
============

Python >=3.6 (Python 2 is not supported).

Install with::

    pip install mypythontools


Python library
==============

**subpackages**

- cicd
- helpers
- pyvueeel

Subpackages are loaded on demand so the import time is as smallest as possible.

Import subpackage with this syntax

>>> from mypythontools import helpers

You will meet error if you use it like this::

    import mypythontools
    helpers = mypythontools.helpers


Check modules help or readme docs with examples.

:py:mod:`mypythontools.cicd`
----------------------------

Module with functionality around Continuous Integration and Continuous Delivery.

Subpackages

- build
- deploy
- project_utils
- tests

In project utils you can find many functions for CI/CD, but also pipelining functions that will call them
in defined order.

Why to use this and not Travis or Circle CI? It's local and it's fast. You can setup it as a task in IDE and
if some phase fails, you know it soon and before pushing to repo.
 
You can also import mypythontools in your CI/CD and use it there of course.

:py:mod:`mypythontools.helpers`
-------------------------------

Module help with many various problems.

Subpackages

- config
- misc
- paths
- plots
- property
- type_hints

Subpackages names are self describing and you can find documentation in subpackages docstrings.


:py:mod:`mypythontools.pyvueeel`
--------------------------------

Library helper for applications made in python and Vue.js (frontend) connected with eel library.


Tools
=====

There are a lot of stuff that's not in python library (installable via pip), but still on GitHub repository.

Link where you can find that content:

https://github.com/Malachov/mypythontools/tree/master/content

Link where you can read about how to use it:

https://mypythontools.readthedocs.io/#content

Some examples of what you can find only on GitHub

project-starter
---------------

Project scaffolding fast and easy.

Download project-starter from

https://github.com/Malachov/mypythontools/tree/master/content/project-starter

(You may need to download all mypythontools repository in zip)

And start developing.

In your IDE do bulk renaming across files and replace `SET_YOUR_NAME` with name of your app / library.

This starter is for vue-eel applications (desktop as well as web) but also for python libraries that will be
stored on PyPi.


If it's python library, delete `gui` folder.

If it's app with gui, delete `setup.py`, `__init__.py` and remove **Installation** and **Modules** from
README. Also, from assets delete `mdi.css` if not using icons and `formulate.css` if not using **vue
formulate**. In `package.json` uncomment library you will be using.

Install used python libraries via `pip install -r requirements.txt` and install JS libraries as well with
`npm install` in folder where package.json is.

To run an app in develop mode, you have to run both frontend and python. Run frontend with debugging
app.py (do not run, just debug). Then run frontend with `npm run serve` in gui folder (or use Task explorer if
using VS Code). Open your favorite browser and open

http://localhost:8080

It's recommended to use Vue.js devtools extension where you can see what component is on cursor, edit props
values or see list of all used mutations.

In opened app, there is a little help button where there is simple overview about how to develop with these
tools.

Delete is faster than write, so there is many working examples like for example plot, various formatting (flex
row, flex column), settings panel, function call from python to js and vice versa or automatic alerting from
python. If you want to see how some example is working, just use **ctrl + F** in IDE or check components for
its props.

This is how the example looks like

.. image:: /_static/project-starter-gui.png
    :width: 620
    :alt: project-starter-gui
    :align: center

**Docs**

It includes docs structure for sphinx docs generations from docstrings. Edit first few lines in conf.py,
index.rst, navi.html and if you want, add static files like logo to `\\_static`.

Usually used with https://readthedocs.org/ free hosting that trigger deploys automatically after pushing to
master. Because of correct relative redirecting in index.rst and navi.html use for readthedocs /path/ before
relative link to other module.

It's also necessary to generate other modules rst files for other pages, but it's if using `push_script.py` as
CI/CD (see below), it's generated automatically via `apidoc`.

It's recommended to use with `sphinx-alabaster-css` (see below).

**CI/CD**

It also includes GitHub actions yml file for pushing codecov coverage file (without token) and .travis.yml for
Travis CI. You don't need those files and can you can delete it.

There is file `push_script.py` in folder `utils` which personally is better (faster) than travis and can do
most of what you want from CI like run pipeline - running tests / generate docs / increment version / push to
GitHub / push to pypi.

Check utils module for more information.

**IDE files**

It also includes some default project specific
 settings for VS Code. You can also delete it.

If developing py - vue - eel app this is the recommended way, but if you want to build just what is necessary
from scratch, you can use this tutorial

https://mypythontools.readthedocs.io/mypythontools.pyvueeel.html#mypythontools.pyvueeel.help_starter_pack_vue_app

requirements
------------

Install many libraries at once (no need for Anaconda). Download `requirements.txt` file from
https://github.com/Malachov/mypythontools/tree/master/content/requirements and in that folder use::

    pip install -r requirements.txt

It's good for python libraries that other users with different versions of libraries will use. If not
standalone application where freezing into virtual env is good idea - here is possible to use these
requirements with using --upgrade from time to time to be sure that your library will be working for
up-to-date version of dependencies.

sphinx-alabaster-css
--------------------

Its good idea to generate documentation from code. If you are using sphinx and alabaster theme, you can use
this css file for formatting.

Tested on readthedocs hosting (recommended).

CSS are served from GitHub, and it's possible to change on one place and edit how all projects docs look like
at once.

Just add this to sphinx conf.py::

>>> html_css_files = ["https://malachov.github.io/readthedocs-sphinx-alabaster-css/custom.css"]

Also, of course if you want you can download it and use locally from project if you need.

Result should look like this

.. image:: /_static/sphinx-alabaster-css.png
    :width: 620
    :alt: sphinx-alabaster-css
    :align: center

Tasks
-----

There are VS Code tasks examples in utils and build module, but here is small tutorial how to use it. Run
command `Tasks: Open User Tasks`, add tasks from github/content/tasks or if you have no task yet, you can
copy / paste all.

Install extension **Task Explorer**

On root copy folder `utils` from content/tasks

You are ready to go. You should see something like this

.. image:: /_static/tasks.png
    :width: 620
    :alt: tasks
    :align: center

You can do CI / CD pipeline or Build app with one click now.
"""

__version__ = "0.1.1"

__author__ = "Daniel Malachov"
__license__ = "MIT"
__email__ = "malachovd@seznam.cz"
