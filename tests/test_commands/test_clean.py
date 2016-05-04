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
        cls.casa = drivecasa.Casapy(echo_to_stdout=False)

    def setUp(self):
        self.output_dir = os.path.join(drivecasa.default_test_ouput_dir,
                                       'clean_output')
        self.testvis_single = test_data.ami_vis_paths[0]
        self.testvis_multiple = test_data.ami_vis_paths
        # Ensure that the output dir will be created if not already present
        # (Also deletes the output ms if present)
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)
        self.clean_args = {"spw": '0:0~5',
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
                                       vis_paths=self.testvis_single,
                                       out_dir=self.output_dir+'/dirty_map',
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

    def test_clean_map(self):
        script = []
        expected_maps = commands.clean(script,
                                       vis_paths=self.testvis_single,
                                       out_dir=self.output_dir+'/clean_map',
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

    def test_multivis_clean_map(self):
        script = []
        expected_maps = commands.clean(script,
                                       vis_paths=self.testvis_multiple,
                                       out_dir=self.output_dir+'/mvclean_map',
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

    # def

