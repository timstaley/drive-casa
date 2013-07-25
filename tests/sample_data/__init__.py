import os

_test_data_dir = os.path.dirname(__file__)


# _ami_uvfits_basename = 'SWIFT_541371-121212.fits'

_ami_uvfits_basenames = ['SWIFT_544784-130104.fits', 'SWIFT_544784-130106.fits']

_ami_vis_basenames = ['SWIFT_544784-130104.ms', 'SWIFT_544784-130106.ms']

_ami_cleaned_img_basename = 'SWIFT_544784-130104.clean.image'

ami_uvfits_paths = [os.path.abspath(os.path.join(_test_data_dir, bname))
                    for bname in _ami_uvfits_basenames]

ami_vis_paths = [os.path.abspath(os.path.join(_test_data_dir, bname))
                    for bname in _ami_vis_basenames]

ami_cleaned_img = os.path.abspath(os.path.join(_test_data_dir,
                                               _ami_cleaned_img_basename))

