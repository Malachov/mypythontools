# -*- mode: python ; coding: utf-8 -*-
my_path = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parents[1]

site_packages_path = Path(eel.__file__).parents[1]

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

import sys
from pathlib import Path
import os
import inspect
import sysconfig

sys.setrecursionlimit(5000)
block_cipher = None

my_file = my_path / main_file

a = Analysis([my_file],
             pathex=[my_path.as_posix()],
             binaries=[],
             datas=add_datas,
             hiddenimports=add_hidden_imports,
             hookspath=[],
             runtime_hooks=[my_path / 'build_tools' / 'env_vars.py'],
             excludes=add_ignored_packages,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=name,
          debug=debug,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=console,
          icon=icon)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='app')
