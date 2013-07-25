import os

def ensure_dir(dirname):
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
    with open(filename, 'w') as fp:
        fp.write('\n'.join(script))

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

