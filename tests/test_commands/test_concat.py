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
        cls.casa = drivecasa.Casapy(echo_to_stdout=False)

    def setUp(self):
        self.output_dir = os.path.join(drivecasa.default_test_ouput_dir,
                                       'concat_output')
        self.testvis_list = test_data.ami_vis_paths
        # Ensure that the output dir will be created if not already present
        # (Also deletes the output ms if present)
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_default(self):
        script = []
        expected_ms = commands.concat(
                                    script,
                                    self.testvis_list,
                                    out_dir=self.output_dir)
        # Manually ensure target does not pre-exist
        if os.path.isdir(expected_ms):
             shutil.rmtree(expected_ms)
        # Test in usual case, not-preexisting
        casa_out, errs = self.casa.run_script(script)
        self.assertTrue(os.path.isdir(expected_ms))

    def test_unicode(self):
        script = []
        unicode_list = [unicode(v) for v in self.testvis_list]
        expected_ms = commands.concat(
                                    script,
                                    unicode_list,
                                    out_dir=self.output_dir)
        print expected_ms
        # Manually ensure target does not pre-exist
        if os.path.isdir(expected_ms):
             shutil.rmtree(expected_ms)
        # Test in usual case, not-preexisting
        casa_out, errs = self.casa.run_script(script)
        print '\n'.join(casa_out)
        self.assertTrue(os.path.isdir(expected_ms))
