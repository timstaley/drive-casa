import os

def ensure_dir(dirname):
    """
    Ensure directory exists.

    Roughly equivalent to `mkdir -p`
    """
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def derive_out_path(in_path, out_dir, out_extension='',
                    strip_in_extension=True):
    """Derives path resulting from replacing extension suffix and moving dir.

    If the out_dir is specified as 'None' then it is assumed that the
    new file should be located in the same directory as the original.

    If the resulting output path is identical to the input path, this
    raises an exception.

    NB the extension should be supplied including the '.' prefix.
    """
    if out_dir is None:
        out_dir = os.path.dirname(in_path)

    basename = os.path.basename(in_path)
    if strip_in_extension:
        basename = os.path.splitext(basename)[0]

    out_path = os.path.join(out_dir, basename + out_extension)
    if os.path.abspath(out_path) == os.path.abspath(in_path):
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