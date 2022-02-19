"""
Common functions for Python / Vue / Eel project.

It contains functions for running eel, overriding eel.expose decorator, converting json to correct python
format or transform data into form for vue tables and plots.

Go on

https://mypythontools.readthedocs.io/#project-starter

for example with working examples.

Image of such an app

.. image:: /_static/project-starter-gui.png
    :width: 620
    :alt: project-starter-gui
    :align: center
"""

from mypythontools.pyvueeel._pyvueeel import (
    expose,
    eel,
    expose_error_callback,
    json_to_py,
    run_gui,
    to_table,
    to_vue_plotly,
)

__all__ = [
    "expose",
    "eel",
    "expose_error_callback",
    "json_to_py",
    "run_gui",
    "to_table",
    "to_vue_plotly",
]
