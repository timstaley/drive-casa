"""
Short routines which produce CASA expressions from various data-structures.
"""


def circular_mask_string(centre_ra_dec_posns, aperture_radius="1arcmin"):
    """Get a mask string representing circular apertures about (x,y) tuples"""
    mask = ''
    if centre_ra_dec_posns is None:
        return mask
    for coords in centre_ra_dec_posns:
        mask += 'circle [ [ {x} , {y}] , {r} ]\n'.format(
                          x=coords[0], y=coords[1], r=aperture_radius)
    return mask


def box_mask_string(centre_pix_posns, width):
    """Get a mask string representing box apertures about (x,y) tuples"""
    mask = ''
    if centre_pix_posns is None:
        return mask
    for coords in centre_pix_posns:
        mask += 'box [ [{lx}pix , {ly}pix]  , [{hx}pix, {hy}pix] ]\n'.format(
                          lx=coords[0] - width / 2, ly=coords[1] - width / 2,
                          hx=coords[0] + width / 2, hy=coords[1] + width / 2,)
    return mask


def astropy_skycoord_as_casa_direction(skycoord):
    """
    Generates a CASA `me.direction` corresponding to given sky-coordinates.

    Args:
        skycoord (astropy.coordinates.SkyCoord): Sky position

    Returns (str): casa `me.direction` instantiation expression.

    """
    return "me.direction('J2000', '{}deg', '{}deg')".format(
        skycoord.ra.degree, skycoord.dec.degree)


def astropy_time_as_casa_epoch(time):
    """
    Args:
        time (astropy.time.Time): Reference time

    Returns (str): casa `me.epoch` instantiation expression
        (uses UTC conversion from astropy Time).
    """
    return "me.epoch('UTC', '{}')".format(
        time.utc.datetime.strftime("%Y/%m/%d/%H:%M:%S"))