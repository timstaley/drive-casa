"""
Define some subroutines which we pre-load into the CASA environment.

These allow us to e.g. define subroutines for converting a custom file-format
into native Python data-structures.
"""

# Load the columns from an antenna-list config file into lists.
def_load_antennalist = """
def drivecasa_load_antennalist(antennalist_path):
    with open(antennalist_path, 'r') as f:
        x = [];
        y = [];
        z = [];
        d = []
        lines = f.readlines()
        for l in lines:
            items = l.split()
            if (items[0] != '#'):
                x.append(float(items[0]))
                y.append(float(items[1]))
                z.append(float(items[2]))
                d.append(float(items[3]))
    return x, y, z, d
    """

all_subroutines = (
    def_load_antennalist,
)
