- [ ] Check if coverage from doctest included
- [ ] Update venv outside tests and use it in pyinstaller build
- [ ] Add tests to plot from predictit
- [ ] Transform starter to cookiecutter
- [ ] Create GIF of vs code task
- [ ] Better test coverage (doctest in functions + check if in coverage)
- [ ] Check if in pyinstaller better way than hidden imports (add to analysis to build only necessary files)
- [ ] Finish start vue in debug from python

```
    # Try to run npm run serve from app.py if not running

    # try:
    # if devel:

    # If server is not running, it's started automatically
    # import psutil
    # import subprocess

    # import signal
    # already_run = 8080 in [i.laddr.port for i in psutil.net_connections()]

    # if not already_run:

    #     subprocess.Popen(f"cd '{pystore.gui_path.as_posix()}' && npm run serve", stdout=subprocess.PIPE,
    #                      shell=True)
    #     print("\nVue starting, reload page after loaded! \n")
    #     import webbrowser
    #     webbrowser.open('http://localhost:8080/', new=2)
```
