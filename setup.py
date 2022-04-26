#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(
    name='pipe-satellite-data',
    version=__import__('pipe_satellite_data').__version__,
    packages=find_packages(exclude=['test*.*', 'tests'])
)

