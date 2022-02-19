# mypythontools

[![Python versions](https://img.shields.io/pypi/pyversions/mypythontools.svg)](https://pypi.python.org/pypi/mypythontools/) [![PyPI version](https://badge.fury.io/py/mypythontools.svg)](https://badge.fury.io/py/mypythontools) [![Downloads](https://pepy.tech/badge/mypythontools)](https://pepy.tech/project/mypythontools) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Malachov/mypythontools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Malachov/mypythontools/context:python) [![Documentation Status](https://readthedocs.org/projects/mypythontools/badge/?version=latest)](https://mypythontools.readthedocs.io/en/latest/?badge=latest) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![codecov](https://codecov.io/gh/Malachov/mypythontools/branch/master/graph/badge.svg)](https://codecov.io/gh/Malachov/mypythontools)


Some tools/functions/snippets/files used across projects.

It's called mypythontools, but it's also made for you...

Can be used as python library. Things like building the application with pyinstaller, incrementing version,
generating rst files for sphinx docs, pushing to GitHub or deploying to PyPi or other CI/CD functionality,
creating config module or plot data is a matter of calling one function or clicking one button (e.g. Vs Code task).

Many projects - one codebase.

If you are not sure whether the structure of your app will work with this code, check `project-starter` on GitHub
in content folder.

Paths are inferred, but if you have atypical structure or have more projects in cwd, setup necessary paths in paths
module.

There is also some extra stuff, that is not bundled via PyPI (cookiecutter, CSS for readthedocs etc.),
such a content is under the Content topic.


## Links

Official documentation - [readthedocs](https://mypythontools.readthedocs.io/)

Official repo - [GitHub](https://github.com/Malachov/mypythontools)

It's called mypythontools, but it's also made for you...

Usually used from IDE. Used paths are inferred and things like sphinx rst docs generation, building
application with pyinstaller or deploying to PyPi is the matter of calling one function,
or clicking one button (e.g. Vs Code task).

Many projects - one codebase.

If you are not sure whether the structure of your app will work with this code, check `project-starter` on GitHub in content folder.

Paths are inferred, but if you have atypical structure or have more projects in cwd, setup paths in paths module.

There is also some extra stuff, that is not bundled via PyPI (cookiecutter, CSS for readthedocs etc.), 
such a content is in folder Content.

## Installation

Python >=3.6 (Python 2 is not supported).

Install with

```console
pip install mypythontools
```

Python library
==============

**subpackages**

- cicd
- helpers
- pyvueeel

Subpackages are loaded on demand, so the import time is as small as possible.

Import subpackage with this syntax

```python
from mypythontools import helpers
```

You will meet error if you use it like this

<!--phmdoctest-mark.skip-->
```python
import mypythontools
helpers = mypythontools.helpers
```

Check modules help or readme docs with examples.

cicd
----

Module with functionality around Continuous Integration and Continuous Delivery.

Subpackages

- build
- deploy
- project_utils
- tests

In project utils, you can find many functions for CI/CD, but also pipelining functions that will call them
in defined order.

Why to use this and not Travis or Circle CI? It's local and it's fast. You can set up it as a task in IDE and
if some phase fails, you know it soon and before pushing to repo.

You can also import mypythontools in your CI/CD and use it there.

helpers
-------

Module help with many various problems.

Subpackages

- config
- misc
- paths
- plots
- property
- type_hints

Subpackages names are self describing, and you can find documentation in subpackages docstrings.


pyvueeel
--------

Library helper for applications made in python and Vue.js (frontend) connected with eel library.


## Content

There are some other things that are not installed via pip in mypythontools library.

### project-starter

Project scaffolding fast and easy.

Download project-starter from (GitHub)[https://github.com/Malachov/mypythontools/tree/master/content/project-starter] (You may need to download all mypythontools repository in zip)

And start developing.

In your IDE do bulk renaming across files and replace `SET_YOUR_NAME` with name of your app / library.

This starter is for vue-eel applications (desktop as well as web) but also for python libraries that will be stored on PyPi.

**Used as a python library**

If it's python library, delete `gui` folder.

**Used as an application**
It can be opened as web page from explorer, or it can be opened as standalone desktop application (looks similar to electron and require chrome or chromium on the background).

If it's app with gui, delete `setup.py`, `__init__.py` and remove **Installation** and **Modules** from README. Also, from
assets delete `mdi.css` if not using icons and `formulate.css` if not using **vue formulate**. In
`package.json` uncomment library you will be using.

Install used python libraries via `pip install -r requirements.txt` and install JS libraries as well with
`npm install` in folder where package.json is.

To run an app in develop mode, you have to run both frontend and python. Run frontend with debugging app.py (do not run, just debug). Then run frontend with `npm run serve` in gui folder (or use Task explorer if using VS Code). Open your favourite browser and open [http://localhost:8080](http://localhost:8080).

It's recommended to use Vue.js devtools extension where you can see what component is on cursor, edit props values or see list of all used mutations.

In opened app, there is a little help button where there is a simple overview about how to develop with these tools.

Delete is faster than write, so there are many working examples like for example plot, various formatting (flex row, flex column), settings panel, function call from python to JS and vice versa or automatic alerting from python. If you want to see how some example is working, just use **ctrl + F** in IDE or check components for its props.

This is how the example looks like

<div align="center"><img src="docs/source/_static/project-starter-gui.png" width="620" alt="project-starter-gui"/></div>

For a desktop version where the user does not have python installed, you have to build it first. Use mypythontools `build` module (trigger with tasks button).

**Docs**
It includes docs structure for sphinx docs generations from docstrings. Edit first few lines in conf.py, index.rst, navi.html and if you want, add static files like logo to \_static.

Usually used with [readthedocs](https://readthedocs.org/) free hosting that trigger deploys automatically after pushing to master. Because of correct relative redirecting in `index.rst` and `navi.html` use for readthedocs /path/ before relative link to other module.

It's also necessary to generate other modules rst files for other pages. If you are using `push_script.py` as CI/CD (see below), it's generated automatically via `apidoc`.

It's recommended to use with `sphinx-alabaster-css` (see below).

**CI/CD**
Project include `.travis.yml` for Travis CI, but it's not recommended using it. There is file `push_script.py` in folder `utils` which for my use case is better (faster) than travis and can do most of what you want from CI like run pipeline - running tests / generate docs / increment version / push to GitHub / push to PyPi.

You can delete `.travis.yml`. If you want to generate test coverage badge (usually from travis), you can use GitHub actions yml file for pushing codecov coverage file (without token).

Check utils module for more information.

**IDE files**
It also includes some default project specific settings for VS Code. You can also delete it.


### requirements

Install many libraries at once (no need for Anaconda). Download `requirements.txt` file from (GitHub)[https://github.com/Malachov/mypythontools/tree/master/content/requirements] and in that folder use

```
pip install -r requirements.txt
```

It's good for python libraries that other users with different versions of libraries will use. If not standalone application where freezing into virtual env is good idea - here is possible to use these requirements with using --upgrade from time to time to be sure that your library will be working for up-to-date version of dependencies.

### sphinx-alabaster-css

It's a good idea to generate documentation from code. If you are using sphinx and alabaster theme, you can use this CSS file for formatting.

Tested on readthedocs hosting (recommended).

CSS are served from GitHub, and it's possible to change on one place and edit how all projects docs look like at once.

Just add this to sphinx conf.py

```
html_css_files = [
    "https://malachov.github.io/readthedocs-sphinx-alabaster-css/custom.css",
]
```

Also, of course if you want you can download it and use locally from project if you need.

Result should look like this

<div align="center"><img src="docs/source/_static/sphinx-alabaster-css.png" width="620" alt="sphinx-alabaster-css"/></div>

### Tasks

There are VS Code tasks examples in utils and build module, but here is small tutorial how to use it. Run
command `Tasks: Open User Tasks`, add tasks from github/content/tasks or if you have no task yet, you can
copy / paste all.

Install extension **Task Explorer**

On root copy folder `utils` from content/tasks

You are ready to go. You should see something like this

<div align="center"><img src="docs/source/_static/tasks.png" width="620" alt="tasks"/></div>

You can do CI / CD pipeline or Build app with one click now.
