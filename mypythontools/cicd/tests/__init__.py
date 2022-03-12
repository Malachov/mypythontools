"""Module with functions around testing. You can run tests including doctest with generating coverage,
you can generate tests from readme or you can configure tests in conftest with single call."""

from mypythontools.cicd.tests.tests_internal import (
    add_readme_tests,
    deactivate_test_settings,
    run_tests,
    setup_tests,
)

__all__ = ["add_readme_tests", "deactivate_test_settings", "run_tests", "setup_tests"]