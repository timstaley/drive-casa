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

# Can hard-code a default casa-dir here for easy running of unit-tests,
# if required:
default_casa_dir = None  # (If available already via external environment paths)
# default_casa_dir = '/opt/soft/builds/casapy-active'

default_test_ouput_dir = '/tmp/drivecasa-tests'


###########################################################
# Versioning; see also
# http://stackoverflow.com/questions/17583443
###########################################################
try:
    _dist = get_distribution('drive-casa')
    #The version number according to Pip:
    _nominal_version = _dist.version
    if not __file__.startswith(os.path.join(_dist.location, 'drivecasa')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    #The actual copy in use if a custom PYTHONPATH or local dir import is used
    __version__ = 'Local import @ '+os.path.dirname(os.path.abspath(__file__))
else:
    __version__ = _nominal_version