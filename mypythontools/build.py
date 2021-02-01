"""
This module build the app via pyinstaller.
It help to build applications build with eel.
"""

import subprocess
import pathlib
import os
import shutil
import json

import mylogging


def build_app(
        build_settings={
            'console': False,
            'debug': False,
            'name': 'app',
            'main_file': 'app.py',
            'icon': (my_path / 'gui' / 'public' / 'logo.ico').as_posix(),
            'add_hidden_imports': ['bottle_websocket', 'scipy.spatial.transform._rotation_groups']
            'add_ignored_packages': ['tensorflow', 'keras', 'notebook', 'pytest', 'pyzmq', 'zmq', 'sqlalchemy', 'sphinx', 'PyQt5', 'PIL', 'matplotlib', 'qt5', 'PyQt5', 'qt4', 'pillow'],
            'add_datas': [((my_path / 'gui' / 'web_builded').as_posix(), 'gui/web_builded')]
        },
        build_web=1, remove_last_builds=0):

    spec_settings = f"""
    console = False
    debug = True

    name = 'app'
    main_file = 'app.py'

    icon = (my_path / 'gui' / 'public' / 'logo.ico').as_posix()

    add_hidden_imports = [
        'bottle_websocket',
        'scipy.spatial.transform._rotation_groups',
    ]

    add_ignored_packages = ['tensorflow', 'keras', 'notebook', 'pytest', 'pyzmq', 'zmq', 'sqlalchemy', 'sphinx', 'PyQt5', 'PIL', 'matplotlib', 'qt5', 'PyQt5', 'qt4', 'pillow']

    add_datas = [((my_path / 'gui' / 'web_builded').as_posix(), 'gui/web_builded')]
    """

    root_path = misc.root_path

    if remove_last_builds:
        try:
            shutil.rmtree('build', ignore_errors=True)
            shutil.rmtree('dist', ignore_errors=True)
        except Exception:
            pass

    # Build JS to static asset
    if build_web:
        os.chdir(root_path / 'gui')
        subprocess.run(['npm', 'run', 'build'], shell=True)

    # Build py to exe
    os.chdir(root_path)
    subprocess.run(['pyinstaller', '-y', 'build_tools/app.spec'], shell=True)


def _generate_spec_file():
    with open('app.spec') as spec_file:
        spec_file.write(
"""
