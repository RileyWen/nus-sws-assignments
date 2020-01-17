#!/usr/bin/python
"""
Running Python apps on Bluemix
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='sunimal-flask',
    version='1.0.0',
    description='simple app for IBM personality insights with Flask',
    license='Apache-2.0'
)
