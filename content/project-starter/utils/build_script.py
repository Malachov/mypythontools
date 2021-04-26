import mypythontools


if __name__ == "__main__":

    mypythontools.build.build_app(
        preset="eel",
        console=True,  # True if develop, False in prod
        debug=True,  # True if develop, False in prod
        build_web=True,
        cleanit=False,
        icon=None,  # "logo.ico"
        datas=[],  # Example: [(file1, "file1")]
        ignored_packages=[
            # Can be dependencies of imported libraries
            "tensorflow",
            "pyarrow",
            "keras",
            "notebook",
            "pytest",
            "pyzmq",
            "zmq",
            "sqlalchemy",
            "sphinx",
            "PyQt5",
            "qt5",
            "PyQt5",
            "qt4",
            "pillow",
        ],
        hidden_imports=[
            # If app not working, set console to True, open in console and then add library that's missing
        ],
    )
