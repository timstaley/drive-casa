==========
drive-casa
==========
A Python package for scripting the NRAO CASA_ pipeline routines (``casapy``).

`drive-casa` provides an interface to allow dynamic
interaction with CASA from a *separate* Python process. For example,
one can spawn an instance of ``casapy``, send it some data reduction
commands to run (while saving the logs for future reference),
do some external analysis on the results,
and then run some more casapy routines.
All from within a generic Python 2.7 script. In a virtualenv_.
This is particularly useful when you want to embed use of CASA within a larger
pipeline. 

The package also includes a set of convenience routines which
try to adhere to a consistent style and make it easy to chain together
successive CASA reduction commands;
e.g. `importUVFITS -> Perform Clean on resulting MeasurementSet`.


Rationale
---------
CASA makes use of an altered version of IPython to provide a
user interface, and all of the routines available are in fact Python functions.
This means it *is* possible to write Python scripts and run them from within
``casapy`` itself. However, there are some compelling reasons not to do so:

- CASA comes bundled with its very own Python installation - until
  CASA 4.2 (Feb 2014) this was Python 2.6, which raised potential Python version
  compatibility issues with Python 2.7.
  This will continue to be a problem if the user works with Python 3.
- The 'bundled installation' model also prevents the standard practice of
  using a virtualenv to provide reasonably well encapsulated and reproducible
  data-reduction environments.
- CASA tasks do not, as far as I can tell, return useful values as standard
  (or even throw exceptions). Instead, since the over-riding assumption is that
  the package will be run in interactive mode,
  all information is written to stderr as part of the logging output, making it
  hard to programmatically verify if a task has completed sucessfully.
  `drive-casa` attempts to solve this by parsing the log output for 'SEVERE'
  warnings - the user may then choose to throw an exception when
  it is sensible to do so.
- If scripting the reduction of large amounts of data in batches, it is 
  often useful to record logging information along with the data output,
  both for purposes of debugging and data provenance.
  As far as I can tell, CASA does not provide an interface to control or
  redirect the logging output once the program has been instantiated.
  `drive-casa` can work-around this issue by simply restarting CASA with a fresh
  logging location specified for each dataset.  


Status
------
I'd say `drive-casa` is in beta. I've used it personally for some time now,
and I'm reasonably happy with the interface, so major breaking changes are
unlikely at this point (no guarantees, but then you can always specify a
``pip install`` of a particular archival version).
I'd be interested to hear if others find it useful, and welcome
any pull requests.

 
Installation
------------
*Requirements*:

- A working installation of ``casapy``.
- `pexpect <http://pypi.python.org/pypi/pexpect/>`_ 
  (As listed in `requirements.txt`, installed automatically when using pip.) 
   
drive-casa is now `pip` installable, simply run::

 pip install drive-casa



Documentation
-------------
Reference documentation can be found at
http://drive-casa.readthedocs.org,
or generated directly from the repository using Sphinx_.

A Brief Example
---------------
Basic usage might go something like this::

   import drivecasa
   casa = drivecasa.Casapy()
   script=[]
   uvfits_path = '/path/to/uvdata.fits'
   vis = drivecasa.commands.import_uvfits(script, uvfits_path)
   clean_args = {   
       "spw": '0:3~7',
       "imsize": [512, 512],
       "cell": ['5.0arcsec'],
       "weighting": 'briggs',
          "robust": 0.5,
       }
   dirty_maps = drivecasa.commands.clean(script, vis, niter=0, threshold_in_jy=1,
                                         other_clean_args=clean_args)
   dirty_map_fits_image = drivecasa.commands.export_fits(script, dirty_maps.image)
   casa.run_script(script) 
   
After which, there should be a dirty map converted to FITS format waiting for 
you.

.. _CASA: http://casa.nrao.edu/
.. _virtualenv: http://www.virtualenv.org/
.. _Sphinx: http://sphinx-doc.org/
