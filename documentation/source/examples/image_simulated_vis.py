from __future__ import print_function

import os

import drivecasa
import drivecasa.commands as commands
from drivecasa.utils import ensure_dir

output_dir = './simulation_output'
ensure_dir(output_dir)

commands_logfile = os.path.join(output_dir, "./casa-clean-commands.log")
output_visibility = os.path.join(output_dir, './foovis.ms')
# output_visibility = os.path.join(output_dir, './vla-sim.MS')
output_image = os.path.join(output_dir, './foo')

if os.path.isfile(commands_logfile):
    os.unlink(commands_logfile)
casa = drivecasa.Casapy(commands_logfile=commands_logfile,
                        echo_to_stdout=True,
                        )
script = []
clean_args = {
   "imsize": [512, 512],
   "cell": ['3.5arcsec'],
}

outmaps = commands.clean(script, output_visibility, niter=100,
                         threshold_in_jy=1e-5,
                         out_path=output_image,
                         other_clean_args=clean_args,
                         overwrite=True)

commands.export_fits(script, outmaps.image, overwrite=True)
casa.run_script(script)