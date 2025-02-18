from setuptools import find_packages, setup

setup(
    name="s3_dynamodb_project",
    packages=find_packages(exclude=["s3_dynamodb_project_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
