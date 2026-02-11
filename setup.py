#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(
    name='pipe-satellite-data',
    version='4.1.0',
    packages=find_packages(exclude=['test*.*', 'tests']),
    install_requires=[
        "ephem~=4.1",
        "jinja2-cli~=0.8",
        "NewlineJSON~=1.0",
        "nose~=1.3",
        "numpy~=1.26",
        "pytest~=7.4",
        "python-dateutil~=2.8",
        "pytz~=2023.3",
        "spacetrack~=1.3",
        "statistics~=1.0.3",
        "udatetime~=0.0.17",
        "ujson~=5.9",
    ],
    extras_require={
        "dev": [
            "flake8"
        ]
    }
)
