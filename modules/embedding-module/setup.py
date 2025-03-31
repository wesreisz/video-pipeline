from setuptools import setup, find_packages

setup(
    name="embedding-module",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "python-json-logger>=2.0.0",
    ],
) 