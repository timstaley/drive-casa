#!/usr/bin/env python

from setuptools import setup

#with open('requirements.txt') as f:
#    required = f.read().splitlines()

setup(
    name="drive-casa",
    version="0.3.1",
    packages=['drivecasa'],
    description="""Some useful CASA scripts, packaged to be callable from elsewhere.""",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/drivecasa",
#    install_requires=required,
)
