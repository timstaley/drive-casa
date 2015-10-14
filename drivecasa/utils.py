import os
import collections

def ensure_dir(dirname):
    """
    Ensure directory exists.

    Roughly equivalent to `mkdir -p`
    """
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def derive_out_path(in_paths, out_dir, out_extension='',
                    strip_in_extension=True,
                    out_prefix=None):
    """
    Derives an 'output' path given some 'input' paths and an output directory.

    In the simple case that only a single path is supplied, this is
    simply the pathname resulting from replacing extension suffix and moving
    dir, e.g.

    ``input_dir/basename.in`` -> ``output_dir/basename.out``

    If the out_dir is specified as 'None' then it is assumed that the
    new file should be located in the same directory as the first
    input path.

    In the case that multiple input paths are supplied, their basenames
    are concatenated, e.g.

        ``in_dir/base1.in`` + ``in_dir/base2.in``
            -> ``out_dir/base1_base2.out``

    If the resulting output path is identical to any input path, this
    raises an exception.

    NB the extension should be supplied including the '.' prefix.
    """
    in_paths = listify(in_paths)
    if out_dir is None:
        out_dir = os.path.dirname(in_paths[0])

    in_basenames = [os.path.basename(ip) for ip in in_paths]
    if strip_in_extension:
        in_basenames = [ os.path.splitext(bn)[0] for bn in in_basenames ]


    out_basename = '_'.join(in_basenames)
    if out_prefix:
        out_basename = out_prefix+out_basename
    out_path = os.path.join(out_dir, out_basename + out_extension)
    for ip in in_paths:
        if os.path.abspath(out_path) == os.path.abspath(ip):
            raise RuntimeError(
               'Specified path derivation results in output overwriting input!')
    return out_path

def save_script(script, filename):
    """Save a list of casa commands as a text file"""
    with open(filename, 'w') as fp:
        fp.write('\n'.join(script))

def get_circular_mask_string(centre_ra_dec_posns, aperture_radius="1arcmin"):
    """Get a mask string representing circular apertures about (x,y) tuples"""
    mask = ''
    if centre_ra_dec_posns is None:
        return mask
    for coords in centre_ra_dec_posns:
        mask += 'circle [ [ {x} , {y}] , {r} ]\n'.format(
                          x=coords[0], y=coords[1], r=aperture_radius)
    return mask

def get_box_mask_string(centre_pix_posns, width):
    """Get a mask string representing box apertures about (x,y) tuples"""
    mask = ''
    if centre_pix_posns is None:
        return mask
    for coords in centre_pix_posns:
        mask += 'box [ [{lx}pix , {ly}pix]  , [{hx}pix, {hy}pix] ]\n'.format(
                          lx=coords[0] - width / 2, ly=coords[1] - width / 2,
                          hx=coords[0] + width / 2, hy=coords[1] + width / 2,)
    return mask

def byteify(input):
    """
    Co-erce unicode to 'bytestring'

    (or string containing unicode, or dict containing unicode)
    Useful when e.g. importing filenames from JSON
    (CASA sometimes breaks if passed Unicode strings.)

    cf http://stackoverflow.com/a/13105359/725650
    """
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def listify(x):
    """
    Ensure x is a (non-string) iterable; if not, enclose in a list.

    Returns:
        x or [x], accordingly.
    """
    if isinstance(x, basestring):
        return [x]
    elif isinstance(x, collections.Iterable):
        return x
    else:
        return [x]