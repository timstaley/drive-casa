"""Just some useful CASA scripts, packaged to be callable from elsewhere."""

from __future__ import absolute_import
import os
import sys
import logging
import json
import itertools
import subprocess

import ami.keys as keys
from drivecasa.casa_env import casapy_env

logger = logging.getLogger(__name__)

def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def process_observation(obs, output_dir, casa_dir):
    """
    Processes a pre-processed observation, creating clean and dirty maps
    for both target and calibrator.

    Args:
     - obs: Dictionary containing path to target UVFITs and calibrator UVFITs,
       plus noise estimates.
     - target_mask: Mask described in CASA string format.
     - output_dir: Parent dir where dataset folders reside.
     - casa_dir: Top dir of CASA installation.

    Returns:
     - obs (currently unchanged input dictionary, but possibly with additional
       updated information in future)

    """


    casa_output_dir = os.path.join(output_dir, 'casa')
    images_dir = os.path.join(output_dir, 'images')

    out_dir = os.path.join(casa_output_dir, str(obs[keys.obs_name]))
    target_mask = get_box_mask_string([(256, 256)], width=256)
    image_with_casapy(obs[keys.target_uvfits],
                      out_dir,
                      images_dir,
                      niter=200,
                      threshold_in_mjy=obs[keys.est_noise_mjy] * 2.5,
                      mask=target_mask,
                      casa_dir=casa_dir
                      )
#                    image_std_dev(image_metadata[Ikeys.target])
#
    image_with_casapy(obs[keys.cal_uvfits],
                      out_dir,
                      images_dir,
                      niter=400,
                      threshold_in_mjy=obs[keys.est_noise_mjy] * 3,
                      mask=get_circular_mask_string([(256, 256)]),
                      casa_dir=casa_dir
                      )
    return obs

def get_circular_mask_string(centre_pix_posns, aperture_radius_pix=5):
    mask = ''
    if centre_pix_posns is None:
        return mask
    for coords in centre_pix_posns:
        mask += 'circle [ [ {x}pix , {y}pix] , {r}pix ]\n'.format(
                          x=coords[0], y=coords[1], r=aperture_radius_pix)
    return mask


def get_box_mask_string(centre_pix_posns, width):
    mask = ''
    if centre_pix_posns is None:
        return mask
    for coords in centre_pix_posns:
        mask += 'box [ [{lx}pix , {ly}pix]  , [{hx}pix, {hy}pix] ]\n'.format(
                          lx=coords[0] - width / 2, ly=coords[1] - width / 2,
                          hx=coords[0] + width / 2, hy=coords[1] + width / 2,)
    return mask

def image_with_casapy(uvfits_filename,
                      casa_output_dir,
                      images_output_dir,
                      niter,
                      threshold_in_mjy,
                      mask=None,
                      casa_dir='/usr/local'):

    uvfits_filename = str(uvfits_filename)

    if mask == None:
        mask = ''
    logger.debug("Imaging UVFITS: %s,\n locals:%s", uvfits_filename, locals())
    ensure_dir(casa_output_dir)
    ensure_dir(images_output_dir)

    clean_args = {
               "spw": '0:3~7',
               "niter": niter,
               "threshold": str(threshold_in_mjy) + 'mJy',
              "imsize": [512, 512],
              "cell": ['5.0arcsec'],
#              "weighting":"uniform",
              "pbcor": False,
#              "minpb": 0 ,
              "weighting": 'natural',
#              "weighting": 'briggs',
#              "robust": 0.5, 
              "psfmode": 'clark',
              "imagermode": 'csclean',
#              "cyclefactor": 0.75,
#              "calready": False, 
              'async': False
              }

    basename = os.path.splitext(os.path.basename(uvfits_filename))[0]

    if not os.path.isfile(uvfits_filename):
        raise ValueError("Something went wrong - could not find uvfits file: "
                         + uvfits_filename)

    clean_script = os.path.join(casa_output_dir, basename + "_casapy_clean_script")
    clean_args["vis"] = os.path.join(casa_output_dir, basename + ".ms")
    casa_output_dirty = os.path.join(casa_output_dir, basename + '.dirty')
    dirty_fits = os.path.join(images_output_dir, basename + '.dirty')
    casa_output_clean = os.path.join(casa_output_dir, basename)
    clean_fits = os.path.join(images_output_dir, basename)

    clean_args["imagename"] = casa_output_clean
    clean_args_w_mask = clean_args.copy()

    clean_args_w_mask["mask"] = mask
    clean_args_dirty = clean_args.copy()
    clean_args_dirty['niter'] = 0
    clean_args_dirty['imagename'] = casa_output_dirty

    with open(clean_script, "wb") as script:
        script.write("importuvfits(fitsfile='{0}', vis='{1}.ms')\n".format(
           uvfits_filename, os.path.join(casa_output_dir, basename)))

        script.write("clean(**{})".format(str(clean_args_dirty)) + "\n")
        script.write("exportfits(imagename='{0}.image', fitsimage='{1}.fits')\n"
                     .format(casa_output_dirty, dirty_fits))

        script.write("clean(**{})".format(str(clean_args_w_mask)) + "\n")
        script.write("exportfits(imagename='{0}.image', fitsimage='{1}.fits')\n"
                     .format(casa_output_clean, clean_fits))


    log_basename = os.path.join(casa_output_dir, basename)
    log_filename = log_basename + ".casa.log"
    cmd = ["casapy",
            '--nologger',
            '--logfile', log_filename,
            '--nogui',
            '-c', clean_script
            ]
    logger.debug(" ".join(cmd))
    with open(log_basename + ".casa.stdout", 'w') as log_stdout:
        with open(log_basename + ".casa.stderr", 'w') as log_stderr:
            subprocess.check_call(cmd,
                                  cwd=casa_output_dir,
                                  env=casapy_env(casa_dir),
                                    stdout=log_stdout,
                                    stderr=log_stderr,
                                    )
