import mypythontools

# Find paths and add to sys.path to be able to import local modules
mypythontools.tests.setup_tests()

from conftest import SET_YOUR_NAME


def test_1():
    SET_YOUR_NAME.test_function()
    assert True
