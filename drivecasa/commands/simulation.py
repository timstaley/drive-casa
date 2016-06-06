"""
Provides convenience functions for composing casapy simulation scripts.
"""
import logging
import os
import shutil

import astropy.units as u

from drivecasa.commands.format import (
    astropy_skycoord_as_casa_direction, astropy_time_as_casa_epoch)
from drivecasa.utils import ensure_dir

logger = logging.getLogger(__name__)

_DRIVECASA_FIELD_NAME = "drivecasa_field0"
_DRIVECASA_SPECTRAL_WINDOW_NAME = "drivecasa_spw0"


def make_componentlist(script, source_list, out_path, overwrite=True):
    """
    Build a componentlist and save it to disk.

    Runs `cl.done()` to clear any previous entries, the `cl.addcomponent`
    for each source in the list, and finally `cl.rename`, `cl.close`.

    cf https://casa.nrao.edu/docs/CasaRef/componentlist-Tool.html

    Typically used when simulating observations.

    Args:
        script (list): List of strings to append commands to.
        source_list: List of (position, flux, frequency) tuples.
            Positions should be :class:`astropy.coordinates.SkyCoord`
            instances, while flux and frequency should be quantities supplied
            using the :mod:`astropy.units` functionality.
        out_path (str): Path to save the component list at
        overwrite (bool): Delete any pre-existing component list at out_path.

    Returns (str):
        Absolute path to the output component list

    """
    out_path = os.path.abspath(out_path)
    if os.path.isdir(out_path):
        if overwrite:
            shutil.rmtree(out_path)
        else:
            logger.warning(
                "Componentlist already exists (and overwrite=False).")
    ensure_dir(os.path.dirname(out_path))

    script.append("cl.done()")
    for (posn, flux, freq) in source_list:
        posn_str = "J2000 {}deg {}deg".format(posn.ra.deg, posn.dec.deg)
        freq_str = "{}Hz".format(freq.to(u.Hz).value)
        script.append(
            "cl.addcomponent(dir='{posn_str}', flux={flux}, fluxunit='Jy',"
            "freq='{freq_str}', shape='point')".format(
                posn_str=posn_str, flux=flux.to(u.Jy).value, freq_str=freq_str
            ))
    script.append("cl.rename('{}')".format(out_path))
    script.append("cl.close()")
    return out_path


def _load_antennalist(script, antennalist_path):
    """
    Load the columns from an antenna-list config file into lists.

    The antenna-list file is assumed to be in XYZ format, similar to those
    distributed with CASA.

    The list-variable names are hard-coded and simply pushed into the
    casapy Python environment, rather than trying to provide flexibility
    about what to call them. This gives simple usage and matches the typical
    casapy approach of 'work with one thing (and only one thing) at a time'.

    The list-variable names are prefixed by `_dc_` in an attempt to avoid
    any risk of name-clashes.

    The actual parsing is performed by a subroutine to keep the scripts
    minimal.
    """
    path = os.path.abspath(antennalist_path)
    cmd = (
        "_dc_ant_x, _dc_ant_y, _dc_ant_z, _dc_ant_d = "
        "drivecasa_load_antennalist('{}')".format(path))
    script.append(cmd)


def setconfig(script, telescope_name, antennalist_path):
    """
    Configure the telescope parameters with `sm.setconfig`

    cf https://casa.nrao.edu/docs/CasaRef/simulator.setconfig.html

    Args:
        script (list): casapy script-list
        telescope_name (str): e.g. 'VLA'
        antennalist_path (str): antenna-list config file

    """
    _load_antennalist(script, antennalist_path)
    cmd = ("sm.setconfig("
           "telescopename='{telescope}',"
           "x=_dc_ant_x, "
           "y=_dc_ant_y, "
           "z=_dc_ant_z,"
           "dishdiameter=_dc_ant_d,"
           "mount='alt-az',"
           "coordsystem='local',"
           "referencelocation=me.observatory('{telescope}')"
           ")".format(
        telescope=telescope_name,
    ))
    script.append(cmd)


def setpb(script, telescope_name, primary_beam_hwhm, frequency):
    """
    Configure Gaussian primary beam parameters for a measurement simulation.

    Runs `vp.setpbgauss` followed by `sm.setvp` to activate it.
    cf
    https://casa.nrao.edu/docs/CasaRef/vpmanager.setpbgauss.html
    https://casa.nrao.edu/docs/CasaRef/simulator.setvp.html

    Args:
        script (list): casapy script-list
        telescope_name (str): e.g. 'VLA'
        primary_beam_hwhm (astropy.units.Quantity): HWHM radius, i.e.
            angular radius to point of half-maximum in primary beam.
        frequency (astropy.units.Quantity): Reference frequency for primary
            beam.

    """
    cmd = ("vp.setpbgauss("
           "telescope='{telescope}', "
           "dopb=True, "
           "halfwidth='{pbhwhm_deg}deg',"
           "reffreq='{freq_hz}Hz'"
           ")".format(
        telescope=telescope_name,
        pbhwhm_deg=primary_beam_hwhm.to(u.degree).value,
        freq_hz=frequency.to(u.Hz).value
    ))
    script.append(cmd)
    cmd = ("sm.setvp("
           "dovp=True, "
           ")")
    script.append(cmd)


def setspwindow(script,
                freq_start,
                freq_resolution,
                freq_delta,
                n_channels,
                stokes='XX XY YX YY',
                ):
    """
    Define a spectral window with `sm.setspwindow`.

    cf https://casa.nrao.edu/docs/CasaRef/simulator.setspwindow.html

    Args:
        script (list): casapy script-list
        freq_start (astropy.units.Quantity): Starting frequency for
            spectral window.
        freq_resolution (astropy.units.Quantity): Frequency width of each
            channel.
        freq_delta (astropy.units.Quantity): Frequency increment per
            channel.
        n_channels (int): Number of channels
        stokes (str): Stokes types to simulate
    """
    cmd = ("sm.setspwindow("
           "spwname='{spw_name}', "
           "freq='{freq_start_hz}Hz',"
           "deltafreq='{freq_delta_hz}Hz',"
           "freqresolution='{freq_res_hz}Hz', "
           "nchannels={nchan}, "
           "stokes='{stokes}'"
           ")".format(
        spw_name=_DRIVECASA_SPECTRAL_WINDOW_NAME,
        freq_start_hz=freq_start.to(u.Hz).value,
        freq_res_hz=freq_resolution.to(u.Hz).value,
        freq_delta_hz=freq_delta.to(u.Hz).value,
        nchan=n_channels,
        stokes=stokes,
    ))
    script.append(cmd)


def setfeed(script, mode='perfect X Y', pol=['']):
    """
    Set feed polarisation with `sm.setfeed`

    cf https://casa.nrao.edu/docs/CasaRef/simulator.setfeed.html

    Args:
        script (list): casapy script-list
        mode (str): choice between 'perfect R L' and 'perfect X Y'
        pol (str): Polarization (undocumented).
    """
    cmd = ("sm.setfeed("
           "mode='{}', "
           "pol={}"
           ")".format(mode, pol))
    script.append(cmd)


def setfield(script, pointing_centre):
    """
    Set pointing centre of simulated field of view with `sm.setfield`.

    cf https://casa.nrao.edu/docs/CasaRef/simulator.setfield.html

    Args:
        script (list): casapy script-list
        pointing_centre (astropy.coordinates.SkyCoord): Field pointing centre

    """
    cmd = ("sm.setfield("
           "sourcename='{source_name}', "
           "sourcedirection={direction}"
           ")".format(
        source_name=_DRIVECASA_FIELD_NAME,
        direction=astropy_skycoord_as_casa_direction(pointing_centre),
    ))
    script.append(cmd)


def setlimits(script, shadow_limit=1e-3, elevation_limit=15 * u.degree):
    """
    Set shadowing / elevation limits before simulated data are flagged.

    Runs `sm.setlimits`
    cf https://casa.nrao.edu/docs/CasaRef/simulator.setlimits.html

    Args:
        script (list): casapy script-list
        shadow_limit (float): Maximum fraction of geometrically shadowed
            area before flagging occurs
        elevation_limit (astropy.units.Quantity): Minimum elevation angle
            before flagging occurs
    """
    cmd = ("sm.setlimits("
           "shadowlimit={}, "
           "elevationlimit='{}deg')".format(
        shadow_limit, elevation_limit.to(u.degree).value
    ))
    script.append(cmd)


def setauto(script, autocorr_weight=0.0):
    """
    Set autocorrelation weight with `sm.setauto`.

    cf https://casa.nrao.edu/docs/CasaRef/simulator.setauto.html

    Args:
        script (list): casapy script-list
        autocorr_weight (float): Weight to assign autocorrelations

    """
    cmd = ("sm.setauto(autocorrwt={})".format(autocorr_weight))
    script.append(cmd)


def settimes(script, integration_time, reference_time, use_hour_angle=True):
    """
    Set integration time, reference time with `sm.settimes`

    cf https://casa.nrao.edu/docs/CasaRef/simulator.settimes.html

    The 'reference time' defines an epoch, start and stop are defined relative
    to that epoch.


    Args:
        integration_time (astropy.units.Quantity): Time-span of each
            integration.
        reference_time (astropy.time.Time): Reference epoch.
        use_hour_angle (bool): If true, the observation
    """

    ref_time_expr = astropy_time_as_casa_epoch(reference_time)
    integration_time_str = '{}s'.format(integration_time.to(u.s).value)
    cmd = ("sm.settimes("
           "integrationtime='{integration_time_str}', "
           "usehourangle={use_hr_angle},"
           "referencetime={ref_time_expr}"
           ")").format(integration_time_str=integration_time_str,
                       use_hr_angle=use_hour_angle,
                       ref_time_expr=ref_time_expr)
    script.append(cmd)


def observe(script, stop_delay, start_delay=0 * u.s):
    """
    Simulate an empty-field observation's UVW data with `sm.observe`

    cf https://casa.nrao.edu/docs/CasaRef/simulator.observe.html

    Args:
        script (list): casapy script-list
        stop_delay (astropy.units.Quantity): Time-span. Stop observing this
            long after the reference time defined by :func:`.settimes`.
        start_delay (astropy.units.Quantity): Time-span. Start observing this
            long after the reference time defined by :func:`.settimes`.
            (Defaults to 0, so the observation starts immediately at the
            reference time).

    """
    cmd = ("sm.observe("
           "'{field_name}', "
           "'{spw_name}', "
           "starttime='{start}s', "
           "stoptime='{stop}s'"
           ")").format(
        field_name=_DRIVECASA_FIELD_NAME,
        spw_name=_DRIVECASA_SPECTRAL_WINDOW_NAME,
        start=start_delay.to(u.s).value,
        stop=stop_delay.to(u.s).value,
    )
    script.append(cmd)


def _setdata(script):
    """
    Use `sm.setdata` to set the field-id for subsequent processing.

    cf https://casa.nrao.edu/docs/CasaRef/simulator.setdata.html

    Currently unused.

    Args:
        script (list): casapy script-list
    """
    cmd = ("sm.setdata("
           "fieldid=[0]"
           ")")
    script.append(cmd)


def predict(script, component_list_path):
    """
    Use `sm.predict` to add synthetic source-visibilities to a MeasurementSet.

    cf https://casa.nrao.edu/docs/CasaRef/simulator.predict.html

    Args:
        script (list): casapy script-list
        component_list_path (str): Path to component-list (in CASA-table format).

    """
    cmd = "sm.predict(complist='{}')".format(component_list_path)
    script.append(cmd)


def set_simplenoise(script, noise_std_dev):
    """
    Use `sm.setnoise` to assign a simple fixed-sigma noise to visibilities.

    cf https://casa.nrao.edu/docs/CasaRef/simulator.setnoise.html

    NB should be followed by a call to :func:`.corrupt` to actually apply the noise
    addition.

    Args:
        script (list): casapy script-list
        noise_std_dev (astropy.units.Quantity): Standard deviation of the noise
            (units of Jy).
    """
    cmd = "sm.setnoise(simplenoise='{}Jy')".format(
        noise_std_dev.to(u.Jy).value
    )
    script.append(cmd)


def corrupt(script):
    """
    Apply pre-configured simulated noise via `sm.corrupt`

    cf https://casa.nrao.edu/docs/CasaRef/simulator.corrupt.html

    Configure noise first using e.g. :func:`.set_simplenoise`

    Args:
        script (list): casapy script-list
    """
    script.append('sm.corrupt()')


def close_sim(script):
    """
    Flush simulated data to disk and close simulator tool (`sm.close()`)

    cf https://casa.nrao.edu/docs/CasaRef/simulator.close.html
    Args:
        script (list): casapy script-list
    """
    script.append('sm.close()')


def open_sim(script, output_ms_path, overwrite=True):
    """
    Open new MeasurementSet with simulator tool (`sm.open()`)

    cf https://casa.nrao.edu/docs/CasaRef/simulator.open.html

    Args:
        script (list): casapy script-list
        output_ms_path (str): Path to the new CASA MeasurementSet.
        overwrite (bool): Delete any pre-existing component list at out_path.
    """
    output_ms_path = os.path.abspath(output_ms_path)
    if os.path.isdir(output_ms_path):
        if overwrite:
            shutil.rmtree(output_ms_path)
        else:
            logger.warning(
                "Componentlist already exists (and overwrite=False).")
    ensure_dir(os.path.dirname(output_ms_path))
    script.append("sm.open('{}')".format(output_ms_path))
