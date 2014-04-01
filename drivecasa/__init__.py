"""
Interfacing package for scripting CASA from within a larger pipeline.

Comes with several convenience routines that allow chaining of CASA commands,
see :py:mod:`.commands` module.
"""

from __future__ import absolute_import
import os
import sys

import drivecasa.commands
import drivecasa.utils
from drivecasa.casa_env import casapy_env
from drivecasa.interface import Casapy

# Can hard-code a default casa-dir here for easy running of unit-tests,
# if required:
default_casa_dir = None  # (If available already via external environment paths)
# default_casa_dir = '/opt/soft/builds/casapy-active'

default_test_ouput_dir = '/tmp/drivecasa-tests'

