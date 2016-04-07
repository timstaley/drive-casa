from __future__ import print_function
import drivecasa
casa = drivecasa.Casapy()
script = []
uvfits_path = '/path/to/uvdata.fits'
vis = drivecasa.commands.import_uvfits(script, uvfits_path, out_dir='./')
clean_args = {
   "imsize": [512, 512],
   "cell": ['5.0arcsec'],
   "weighting": 'briggs',
      "robust": 0.5,
   }
dirty_maps = drivecasa.commands.clean(script, vis, niter=0, threshold_in_jy=1,
                                     other_clean_args=clean_args)
dirty_map_fits_image = drivecasa.commands.export_fits(script, dirty_maps.image)
print(script)
casa.run_script(script)
