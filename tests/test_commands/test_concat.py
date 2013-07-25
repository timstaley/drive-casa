import unittest
from unittest import TestCase
import drivecasa
import os
import subprocess
import StringIO
import warnings
import shutil

from drivecasa import commands
from .. import sample_data as test_data


class TestConcat(TestCase):
    def shortDescription(self):
        return None

    @classmethod
    def setUpClass(cls):
        casa_dir = os.environ.get('CASA_DIR', drivecasa.default_casa_dir)
        cls.casa = drivecasa.Casapy(casa_dir, echo_to_stdout=False)

    def setUp(self):
        self.output_dir = os.path.join(drivecasa.default_test_ouput_dir,
                                       'concat_output')
        self.testvis = test_data.ami_vis_paths
        # Ensure that the output dir will be created if not already present
        # (Also deletes the output ms if present)
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_default(self):
        script = []
        expected_ms = commands.concat(
                                    script,
                                    self.testvis,
                                    out_dir=self.output_dir)
        print expected_ms
        # Manually ensure target does not pre-exist
        if os.path.isdir(expected_ms):
             shutil.rmtree(expected_ms)
        # Test in usual case, not-preexisting
        casa_out, errs = self.casa.run_script(script)
        print '\n'.join(casa_out)
        self.assertTrue(os.path.isdir(expected_ms))
