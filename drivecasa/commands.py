"""
Provides convenience functions for composing casapy scripts.

While the casapy scripts can be composed by hand, use of convenience
functions helps to prevent syntax errors, and allows for various optional
extras such as forcing overwriting of previous datasets, automatic derivation
of output filenames, etc.

.. note::

    All the command composing functions have a common set of parameters:
     - `script`: The list to which the requested commands should be appended.
     - `out_dir`: The output directory to place output files in, using a derived
       filename.
     - `out_path`: Overrides out_dir, specifies an output file / directory path exactly.
     - `overwrite`: Deletes any pre-existing data at the output location - use with
       caution!

    The composing functions return the paths to the files which should be
    created once the scripted command has been executed.


"""

import os
import shutil
from collections import namedtuple
from drivecasa.utils import ensure_dir, derive_out_path, byteify

class CleanMaps(namedtuple('CleanMaps',
                           ('image', 'model', 'residual', 'psf', 'mask', 'flux'))):
    """
    A namedtuple for bunching together the paths to maps produced by clean.

    Fields: ``('image', 'model', 'residual', 'psf', 'mask')``
    """


def import_uvfits(script, uvfits_path, out_dir=None, out_path=None, overwrite=False):
    """
    Import UVFITS and convert to .ms format.


    If out_path is ``None``, a sensible output .ms directory path will be derived
    by taking the FITS basename, switching the extension to .ms, and locating
    as a subdirectory of ``out_dir``,
    e.g. if ``uvfits_path = '/my/data/obs1.fits', out_dir = '/tmp/junkdata'``
    then the output data will be located at */tmp/junkdata/obs1.ms*.


    **Args:**

    - script: List to which the relevant casapy command line will be appended.
    - uvfits_path: path to input data file.
    - out_dir: Directory in which to place output file. ``None`` signifies
      to place output .ms in same directory as the original FITS file.
    - out_path: Provides an override to the automatic output naming system.
      If this is not ``None`` then the ``out_dir`` arg is ignored and the
      specified path used instead.
    - overwrite: Delete any pre-existing data at the output path (danger!).


    **Returns:** Path to newly converted ms.
    """
    ms_path = out_path
    if ms_path is None:
        ms_path = derive_out_path(uvfits_path, out_dir, '.ms')
    ensure_dir(os.path.dirname(ms_path))
    if overwrite:
        if os.path.isdir(ms_path):
            shutil.rmtree(ms_path)
    # NB Be sure to specify the abspath as seen from current ipython process,
    # in case the user has specified relative path:
    script.append("importuvfits(fitsfile='{0}', vis='{1}')".format(
                     os.path.abspath(uvfits_path), os.path.abspath(ms_path))
                  )
    return ms_path

def concat(script, vis_paths, out_basename=None, out_dir=None, out_path=None,
                             overwrite=False):
    """
    Concatenates multiple visibilities into one.

    By default, output basename is derived by concatenating
    the basenames of the input visibilities, with the prefix `concat_`.
    However, this can result in something very long and unwieldy. Alternatively
    you may specify the exact out_path, or just the out_basename.

    **Returns:** Path to concatenated ms.
    """
    vis_paths = byteify(vis_paths)
    concat_path = byteify(out_path)
    if concat_path is None:
        if out_basename is None:
            basenames = [os.path.splitext(os.path.basename(vp))[0]
                           for vp in vis_paths]
            concnames = 'concat_' + '_'.join(basenames) + '.ms'
        else:
            concnames = out_basename + '.ms'
        concat_path = os.path.join(out_dir, concnames)
    ensure_dir(os.path.dirname(concat_path))
    if overwrite:
        if os.path.isdir(concat_path):
            shutil.rmtree(concat_path)
    abs_vis_paths = [os.path.abspath(v) for v in vis_paths]
    script.append("concat(vis={0}, concatvis='{1}')".format(
                  str(abs_vis_paths), os.path.abspath(concat_path))
                  )
    return concat_path

def clean(script,
          vis_path,
          niter,
          threshold_in_jy,
          mask='',
          other_clean_args=None,
          out_dir=None,
          out_path=None,
          overwrite=False
          ):
    """
    Perform clean process to produce an image/map.

    If out_path is None, then the output basename is derived by
    appending a `.clean` or `.dirty` suffix to the input basename. The various
    outputs are then further suffixed by casa, e.g.
    `foo.clean.image`, `foo.clean.psf`, etc. Since multiple outputs are
    generated, this function returns a dictionary detailing the expected paths.

    NB Attempting to run with pre-existing outputs and ``overwrite=False``
    *will not* throw an error, in contrast to most other routines.
    From the CASA cookbook, w.r.t. the outputs:

        "If an image with that name already exists, it will in general be
        overwritten. Beware using names of existing images however. If the clean
        is run using an imagename where <imagename>.residual and
        <imagename>.model already exist then clean will continue starting from
        these (effectively restarting from the end of the previous clean).
        Thus, if multiple runs of clean are run consecutively with the same
        imagename, then the cleaning is incremental (as in the difmap package)."

    You can override this behaviour by specifying ``overwrite=True``, in which
    case all pre-existing outputs will be deleted.

    NB niter = 0 implies create a  'dirty' map, outputs will be named
    accordingly.

    **Returns**:
    :py:class:`.CleanMaps` namedtuple, listing paths for resulting maps.
    """
    vis_path = byteify(vis_path)
    out_path = byteify(out_path)

    if other_clean_args is None:
        other_clean_args = {}
    clean_args = other_clean_args

    cleaned_path = out_path
    if cleaned_path is None:
        if niter == 0:
            out_ext = '.dirty'
        else:
            out_ext = '.clean'
        cleaned_path = derive_out_path(vis_path, out_dir, out_extension=out_ext)

    clean_args.update({
           'vis':os.path.abspath(vis_path),
           'imagename':os.path.abspath(cleaned_path),
           'niter': niter,
           'threshold': str(threshold_in_jy) + 'Jy',
           'mask': mask
          })
    script.append("clean(**{})".format(repr(clean_args)))

    ensure_dir(os.path.dirname(cleaned_path))
    expected_map_paths = CleanMaps(
        image = cleaned_path + '.image',
        model = cleaned_path + '.model',
        residual = cleaned_path + '.residual',
        psf = cleaned_path + '.psf',
        mask = cleaned_path + '.mask',
        flux = cleaned_path + '.flux',
        )

    if overwrite:
        for path in expected_map_paths:
            if os.path.isdir(path):
                shutil.rmtree(path)
    return expected_map_paths


def export_fits(script, image_path, out_dir=None, out_path=None,
                overwrite=False):
    """
    Convert an image ms to FITS format.

    **Returns:** Path to resulting FITS file.
    """
    fits_path = out_path
    if fits_path is None:
        fits_path = derive_out_path(image_path, out_dir, '.fits',
                                    strip_in_extension=False)
    ensure_dir(os.path.dirname(fits_path))
    # NB Be sure to specify the abspath as seen from current ipython process,
    # in case the user has specified relative path:
    script.append("exportfits(imagename='{0}', fitsimage='{1}', overwrite={2})"
                   .format(os.path.abspath(image_path),
                           os.path.abspath(fits_path),
                           str(overwrite))
                 )
    return fits_path
