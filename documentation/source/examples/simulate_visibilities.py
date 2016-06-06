from __future__ import print_function

import os

import astropy.units as u
import drivecasa
import drivecasa.commands.simulation as sim
from astropy.coordinates import SkyCoord
from astropy.time import Time
from drivecasa.utils import ensure_dir

output_dir = './simulation_output'
ensure_dir(output_dir)

commands_logfile = os.path.join(output_dir, "./casa-commands.log")
component_list_path = os.path.join(output_dir, './sources.cl')
output_visibility = os.path.join(output_dir, './foovis.ms')

if os.path.isfile(commands_logfile):
    os.unlink(commands_logfile)
casa = drivecasa.Casapy(commands_logfile=commands_logfile,
                        echo_to_stdout=True,
                        )
script = []

# For VLA reference numbers, see:
# https://science.nrao.edu/facilities/vla/docs/manuals/oss/performance/fov
# https://science.nrao.edu/facilities/vla/docs/manuals/oss/performance/resolution

# Define some observation parameters:
obs_central_frequency = 3. * u.GHz
obs_frequency_bandwidth = 0.125 * u.GHz
primary_beam_fwhm = (45. * u.GHz / obs_central_frequency) * u.arcmin

# Define the field centre and sources:
centre_ra = 180 * u.deg
centre_dec = 34 * u.deg
# Sources are represented by tuples of (posn, flux, freq)
pointing_centre = SkyCoord(centre_ra, centre_dec)
srclist = [
    (SkyCoord(centre_ra, centre_dec), 1. * u.mJy, obs_central_frequency),
    (SkyCoord(centre_ra, centre_dec + primary_beam_fwhm * 0.5), 1. * u.mJy,
     obs_central_frequency),
]

# Convert the sources to a CASA 'componentlist'
component_list_path = sim.make_componentlist(script, srclist,
                                             component_list_path)

# Open the visibility file
sim.open_sim(script, output_visibility)

# Configure the virtual telescope
sim.setpb(script,
          telescope_name='VLA',
          primary_beam_hwhm=primary_beam_fwhm * 0.5,
          frequency=obs_central_frequency)
sim.setconfig(script,
              telescope_name='VLA',
              antennalist_path='./vla.c.cfg')
sim.setspwindow(script,
                freq_start=obs_central_frequency - 0.5 * obs_frequency_bandwidth,
                freq_resolution=obs_frequency_bandwidth,
                freq_delta=obs_frequency_bandwidth,
                n_channels=1,
                )
sim.setfeed(script, )
sim.setfield(script, pointing_centre)
sim.setlimits(script)
sim.setauto(script)
ref_time = Time('2014-05-01T19:55:45', format='isot', scale='tai')
sim.settimes(script, integration_time=10 * u.s, reference_time=ref_time)

# Generate the visibilities
sim.observe(script, stop_delay=60 * u.s)

sim.predict(script, component_list_path)

sim.set_simplenoise(script, noise_std_dev=1 * u.mJy)
sim.corrupt(script)
sim.close_sim(script)

casa.run_script(script)
