import unittest
from unittest import TestCase
import drivecasa
import os
import subprocess
import StringIO
import warnings
import shutil

from drivecasa import  commands
from .. import sample_data as test_data


class TestExportFits(TestCase):
    def shortDescription(self):
        return None

    @classmethod
    def setUpClass(cls):
        cls.casa = drivecasa.Casapy(echo_to_stdout=False)

    def setUp(self):
        self.output_dir = os.path.join(drivecasa.default_test_ouput_dir,
                                       'exportfits_output')
        self.testfile = test_data.ami_cleaned_img
        # Ensure that the output dir will be created if not already present
        # (Also deletes the output ms if present)
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)


    def test_default_and_overwrite_cases(self):
        script = []
        expected_fits = commands.export_fits(
                                    script,
                                    self.testfile,
                                    out_dir=self.output_dir)
        # Manually ensure target does not pre-exist
        if os.path.isfile(expected_fits):
             shutil.rmtree(expected_fits)
        # Test in usual case, not-preexisting
        self.casa.run_script(script)
        self.assertTrue(os.path.isfile(expected_fits))

        # Now it's there, check we overwrite OK (this is a no-brainer but still)
        script = []
        expected_fits = commands.export_fits(
                                    script,
                                    self.testfile,
                                    out_dir=self.output_dir,
                                    overwrite=True)
        self.casa.run_script(script)

        # Now, attempt to run with overwriting turned off. This both ensures
        # we do not overwrite, and checks the error reporting mechanism:
        script = []
        expected_fits = commands.export_fits(
                            script,
                            self.testfile,
                            out_dir=self.output_dir,
                            # overwrite=False #(By default)
                            )
        with self.assertRaises(RuntimeError):
            self.casa.run_script(script)

    def test_specified_outpath(self):
        script = []
        expected_fits = commands.export_fits(
                                    script,
                                    self.testfile,
                                    out_dir=None,
                                    out_path=self.output_dir + '/exportfitsout.fits')
        # Manually ensure target does not pre-exist
        if os.path.isdir(expected_fits):
             shutil.rmtree(expected_fits)
        # Test in usual case, not-preexisting
        casa_out, errs = self.casa.run_script(script)
        print '\n'.join(casa_out)
        self.assertTrue(os.path.isfile(expected_fits))
