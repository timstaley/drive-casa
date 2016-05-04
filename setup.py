#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

install_requires = [
        'astropy',
        'pexpect>4'
    ]

setup(
    name="drive-casa",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    description="An interfacing package for scripting CASA from an "
                "external pipeline.",
    author="Tim Staley",
    author_email="github@timstaley.co.uk",
    url="https://github.com/timstaley/drive-casa",
    license='BSD 3-clause',
    install_requires=install_requires,
)
