from mypythontools import tests

# Find paths and add to sys.path to be able to import local modules
tests.setup_tests()

from conftest import SET_YOUR_NAME


def test_1():
    SET_YOUR_NAME.test_function()
    assert True
