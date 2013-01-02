from __future__ import absolute_import
import os
import sys
import logging
import json
import itertools
import subprocess

from ami.keys import Keys
from drivecasa.casa_env import casapy_env

def process_data_listing(listings, output_dir, casa_dir):
    """Args:
    listings: Nested dict mapping raw filenames to various useful information,
                e.g. path to calibrated UVFITs.
    output_dir: Parent dir where dataset folders reside.
    casa_dir: Top dir of CASA installation.

    """

    groups = get_grouped_file_listings(listings)
    output_preamble_to_log(groups)
    for grp_name in sorted(groups.keys()):
        files = groups[grp_name]
        grp_dir = os.path.join(os.path.expanduser(output_dir),
                               str(grp_name))
        casa_output_dir = os.path.join(grp_dir, 'casa')
        images_dir = os.path.join(grp_dir, 'images')

        target_mask = get_box_mask_string([(256, 256)], width=256)
        for f in files:
            out_dir = os.path.join(casa_output_dir, str(f[Keys.obs_name]))
            try:
                image_with_casapy(f[Keys.target_uvfits],
                                  out_dir,
                                  images_dir,
                                  niter=200,
                                  threshold_in_jy=f[Keys.est_noise] * 2.5,
                                  mask=target_mask,
                                  casa_dir=casa_dir
                                  )
#                    image_std_dev(image_metadata[IKeys.target])
#
                image_with_casapy(f[Keys.cal_uvfits],
                                  out_dir,
                                  images_dir,
                                  niter=400,
                                  threshold_in_jy=f[Keys.est_noise] * 3,
                                  mask=get_circular_mask_string([(256, 256)]),
                                  casa_dir=casa_dir
                                  )
            except (ValueError, IOError):
                logging.warn("Hit exception imaging target: " + f[Keys.obs_name])
                continue
    return listings

def get_circular_mask_string(xy_pix_tuples, aperture_radius_pix=5):
    mask = ''
    if xy_pix_tuples is None:
        return mask
    for coords in xy_pix_tuples:
        mask += 'circle [ [ {x}pix , {y}pix] , {r}pix ]\n'.format(
                          x=coords[0], y=coords[1], r=aperture_radius_pix)
    return mask


def get_box_mask_string(xy_pix_tuples, width):
    mask = ''
    if xy_pix_tuples is None:
        return mask
    for coords in xy_pix_tuples:
        mask += 'box [ [{lx}pix , {ly}pix]  , [{hx}pix, {hy}pix] ]\n'.format(
                          lx=coords[0] - width / 2, ly=coords[1] - width / 2,
                          hx=coords[0] + width / 2, hy=coords[1] + width / 2,)
    return mask


def get_grouped_file_listings(listings):
    grp_names = list(set([i[Keys.group_name] for i in listings.values()]))
    groups = {}
    for g_name in grp_names:
        grp = [i for i in listings.values() if i[Keys.group_name] == g_name]
        groups[g_name] = grp
    return groups

def output_preamble_to_log(groups):
    logging.info("*************************")
    logging.info("Processing:")
    for key in sorted(groups.keys()):
        logging.info("%s:", key)
        for f in groups[key]:
            logging.info("\t %s", f[Keys.obs_name])
        logging.info("--------------------------------")
    logging.info("*************************")


def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)



def image_with_casapy(uvfits_filename,
                      casa_output_dir,
                      images_output_dir,
                      niter,
                      threshold_in_jy,
                      mask=None,
                      casa_dir='/usr/local'):

    uvfits_filename = str(uvfits_filename)

    if mask == None:
        mask = ''

    logging.debug("Imaging locals:%s", locals())
    ensure_dir(casa_output_dir)
    ensure_dir(images_output_dir)

    clean_args = {
               "spw": '0:3~7',
               "niter": niter,
               "threshold": str(threshold_in_jy * 1000.0) + 'mJy',
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



    log_filename = basename + ".casa.log"
    cmd = ["casapy",
            '--nologger',
            '--logfile', log_filename,
            '--nogui',
            '-c', clean_script
            ]

    logging.debug(" ".join(cmd))
    subprocess.check_call(cmd,
                          cwd=casa_output_dir,
                          env=casapy_env(casa_dir),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            )
