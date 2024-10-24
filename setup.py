#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(
    name='pipe-satellite-data',
    version='3.1.1',
    packages=find_packages(exclude=['test*.*', 'tests'])
)

