from unittest import TestCase
import drivecasa
import os
import shutil

import astropy.units as u
import drivecasa.commands.simulation as sim
from astropy.coordinates import SkyCoord
from astropy.time import Time
from .. import sample_data as test_data


class TestComponentList(TestCase):
    def shortDescription(self):
        return None

    @classmethod
    def setUpClass(cls):
        cls.casa = drivecasa.Casapy(echo_to_stdout=True)

    def setUp(self):
        self.output_dir = os.path.join(drivecasa.default_test_ouput_dir,
                                       'componentlist_test')
        # Ensure that the output dir will be created if not already present
        # (Also deletes the output ms if present)
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def test_componentlist(self):
        srclist = [
            (SkyCoord(10 * u.deg, 5 * u.deg), 1.5 * u.mJy, 3 * u.GHz,),
            (SkyCoord(10 * u.deg, 5.1 * u.deg), 15 * u.mJy, 2.5 * u.GHz,),

        ]
        out_path = os.path.join(self.output_dir, "foo.cl")
        script = []
        sim.make_componentlist(script, srclist, out_path)
        # Need to insert these prior to `cl.close()`
        script.insert(-1, 'print cl.length()')
        script.insert(-1, 'print cl.getcomponent(0)')
        self.casa.run_script(script)
        out, err = self.casa.run_script([])
        self.assertTrue(os.path.isdir(out_path))


class TestMeasurementSimulation(TestCase):
    def setUp(self):
        self.casa = drivecasa.Casapy(echo_to_stdout=True)
        self.output_dir = os.path.join(drivecasa.default_test_ouput_dir,
                                       'ms_generation_test')
        self.output_ms_path = os.path.join(self.output_dir,
                                           'foobar.ms')
        # Ensure that the output dir will be created if not already present
        # (Also deletes the output ms if present)
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def test_antennalist_load(self):
        script = []
        sim._load_antennalist(script, test_data.vla_antennalist)
        script.append("print _dc_ant_x")
        self.casa.run_script(script)

    def test_setconfig(self):
        script = []
        script.append("sm.open('{}')".format(self.output_ms_path))
        sim.setconfig(script,
                      telescope_name='VLA',
                      antennalist_path=test_data.vla_antennalist)
        self.casa.run_script(script)

    def test_setconfig(self):
        script = []
        sim.setpb(script,
                  telescope_name='VLA',
                  primary_beam_hwhm=1.5 * u.degree,
                  frequency=2.5 * u.GHz)
        self.casa.run_script(script)

    def test_setspwindow(self):
        script = []
        sim.setspwindow(script,
                        freq_start=2.5 * u.GHz,
                        freq_resolution=125 * u.kHz,
                        freq_delta=125 * u.kHz,
                        n_channels=1,
                        )
        self.casa.run_script(script)

    def test_simobserve_subcommands_syntax(self):
        """
        Check all the commands to configure a simulated observation will run OK.

        (Not the same as ensuring they do the right thing!)
        """
        script = []
        sim.open_sim(script, self.output_ms_path)
        sim.setpb(script,
                  telescope_name='VLA',
                  primary_beam_hwhm=1.5 * u.degree,
                  frequency=2.5 * u.GHz)
        sim.setconfig(script,
                      telescope_name='VLA',
                      antennalist_path=test_data.vla_antennalist)
        sim.setspwindow(script,
                        freq_start=2.5 * u.GHz,
                        freq_resolution=125 * u.kHz,
                        freq_delta=125 * u.kHz,
                        n_channels=1,
                        )
        sim.setfeed(script, )
        sim.setfield(script, SkyCoord(192, -35, unit='deg'))
        sim.setlimits(script)
        sim.setauto(script)
        ref_time = Time('2014-05-01T19:55:45', format='isot', scale='tai')
        sim.settimes(script, integration_time=10 * u.s, reference_time=ref_time)
        sim.observe(script, stop_delay=60 * u.s)
        sim.set_simplenoise(script, noise_std_dev=0.1 * u.Jy)
        sim.corrupt(script)
        sim.close_sim(script)
        self.casa.run_script(script)
