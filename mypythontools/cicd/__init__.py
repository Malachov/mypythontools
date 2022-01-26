"""Module with functionality around Continuous Integration and Continuous Delivery.

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
"""
from mypythontools.cicd import build
from mypythontools.cicd import deploy
from mypythontools.cicd import project_utils
from mypythontools.cicd import tests
from mypythontools.cicd import venvs

__all__ = ["build", "deploy", "project_utils", "tests", "venvs"]
