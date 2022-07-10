"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""

from mypythontools_cicd.cicd import cicd_pipeline, default_pipeline_config


if __name__ == "__main__":
    default_pipeline_config.deploy = True
    default_pipeline_config.test.sync_test_requirements = ["requirements/requirements_tests.txt"]

    # default_pipeline_config.do_only = "deploy"

    # All the parameters can be overwritten via CLI args
    cicd_pipeline(config=default_pipeline_config)
