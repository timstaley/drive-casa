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


class TestClean(TestCase):
    def shortDescription(self):
        return None

    @classmethod
    def setUpClass(cls):
        casa_dir = os.environ.get('CASA_DIR', drivecasa.default_casa_dir)
        cls.casa = drivecasa.Casapy(casa_dir, echo_to_stdout=False)

    def setUp(self):
        self.output_dir = os.path.join(drivecasa.default_test_ouput_dir,
                                       'clean_output')
        self.testvis = test_data.ami_vis_paths[0]
        # Ensure that the output dir will be created if not already present
        # (Also deletes the output ms if present)
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)
        self.clean_args = {   "spw": '0:3~7',
                              "imsize": [512, 512],
                              "cell": ['5.0arcsec'],
                              "pbcor": False,
                    #           "weighting": 'natural',
                                 "weighting": 'briggs',
                                 "robust": 0.5,
                    #          "weighting":'uniform',
                              "psfmode": 'clark',
                              "imagermode": 'csclean',
                              }

    def test_dirty_map(self):
        script = []
        expected_maps = commands.clean(script,
                                       vis_path=self.testvis,
                                       out_dir=self.output_dir,
                                       niter=0,
                                       threshold_in_jy=1,
                                       mask='',
                                       other_clean_args=self.clean_args,
                                       overwrite=True)

        print expected_maps
        # Manually ensure target does not pre-exist
        for map in expected_maps:
            if os.path.isdir(map):
                 shutil.rmtree(map)
        # Test in usual case, not-preexisting
        casa_out, errs = self.casa.run_script(script)
#         print '\n'.join(casa_out)
        self.assertTrue(os.path.isdir(expected_maps.image))

#    @unittest.skip
    def test_clean_map(self):
        script = []
        expected_maps = commands.clean(script,
                                       vis_path=self.testvis,
                                       out_dir=self.output_dir,
                                       niter=500,
                                       threshold_in_jy=0.2 / 1000.,
                                       mask='',
                                       other_clean_args=self.clean_args,
                                       overwrite=True)

        print expected_maps
        # Manually ensure target does not pre-exist
        for map in expected_maps:
            if os.path.isdir(map):
                 shutil.rmtree(map)
        # Test in usual case, not-preexisting
        casa_out, errs = self.casa.run_script(script)
        print '\n'.join(casa_out)
        self.assertTrue(os.path.isdir(expected_maps.image))

