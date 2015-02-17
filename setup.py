#!/usr/bin/env python

from setuptools import setup

setup(
    name="drive-casa",
    version="0.6.2",
    packages=['drivecasa'],
    description="""An interfacing package for scripting CASA from within a larger pipeline.""",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/drive-casa",
    license='BSD 3-clause',
    install_requires=['pexpect'],
)
