from unittest import TestCase
import drivecasa
import os
import subprocess
import warnings

from drivecasa.interface import default_casa_dir


class TestCasaInstallation(TestCase):
    """Ensures that casapy is available, either through the pre-existing
    environment path, or via the casapy dir specified to the casapy_env
    function."""

    def shortDescription(self):
        return None

    def setUp(self):
        self.env = drivecasa.casapy_env(default_casa_dir)
        self.known_good_casa_versions = ['5.1.2-rel-4']

    def test_casa_version(self):
        cmd = ['casa-config', '--version']

        output = subprocess.check_output(cmd, env=self.env
                                         )
        version = output.strip()
        print "Version:", version
        self.assertNotEqual(None, version)
        if version not in self.known_good_casa_versions:
            warnings.warn(
                "This library has not been tested against CASA version " +
                version + ", known good versions are:\n"
                + str(self.known_good_casa_versions)
            )
