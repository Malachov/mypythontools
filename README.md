mypythontools
=============

Some tools/functions/snippets used across projects.

Usually used from IDE. Root path is infered and things like docs generation on pre-commit
hooks, building application with pyinstaller or deploying to Pypi is matter of calling one function.

Many projects - one codebase.

If you are not sure whether structure of app that will work with this code, there is python starter repo
on [github](https://github.com/Malachov/my-python-starter)

Paths are infered, but if you have atypical structure or have more projects in cwd, use `mypythontools.misc.set_paths()`.