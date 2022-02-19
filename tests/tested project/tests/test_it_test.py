from mypythontools.cicd.tests import setup_tests

setup_tests()

from project_lib.app import hello


def test_hello():
    assert hello() == "hello"
