"""
Drive-casa is an interfacing package for scripting of CASA from a separate
Python process (see :ref:`introduction`).

The package includes several convenience routines that allow chaining of CASA
commands, see :py:mod:`.commands` module.
"""

from __future__ import absolute_import
import os
import sys

from pkg_resources import get_distribution, DistributionNotFound

import drivecasa.commands
import drivecasa.utils
from drivecasa.casa_env import casapy_env
from drivecasa.interface import Casapy


default_test_ouput_dir = '/tmp/drivecasa-tests'


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
