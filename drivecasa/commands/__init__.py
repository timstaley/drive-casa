"""
This subpackage provides convenience functions for composing casapy data-reduction scripts.

While the casapy scripts can be composed by hand, use of convenience
functions helps to prevent syntax errors, and allows for various optional
extras such as forcing overwriting of previous datasets, automatic derivation
of output filenames, etc.
"""

# Import commonly-used data-reduction commands for convience
# (And backwards compatibility)
from drivecasa.commands.reduction import (
    clean,
    concat,
    export_fits,
    import_uvfits,
    mstransform
)