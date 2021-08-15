import pytest
import mypythontools

mypythontools.tests.setup_tests()


# Setup imports if using some local packages and global variables if you need
@pytest.fixture(autouse=True)
def setup_tests(doctest_namespace):
    my_global_tests_var = 666
    doctest_namespace["my_global_tests_var"] = my_global_tests_var
