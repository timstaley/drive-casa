.. _introduction:

+++++++++++++++++++++++++++
Introduction to drive-casa
+++++++++++++++++++++++++++

A Python package for scripting the NRAO CASA_ pipeline routines (casapy).

drive-casa provides an interface to allow dynamic
interaction with CASA from a *separate* Python process, allowing utilization
of CASA routines alongside other Python packages which may not easily be
installed into the casapy environment.

For example,
one can spawn an instance of casapy, send it some data reduction
commands to run (while saving the logs for future reference),
do some external analysis on the results,
and then run some more casapy routines.
All from within a standard Python script, and preferably from a virtualenv_.
This is particularly useful when you want to embed use of CASA within a larger
pipeline which uses external Python libraries alongside CASA functionality.

drive-casa can be used to run plain-text casapy scripts
directly; alternatively the package includes a set of convenience
routines which try to adhere to a consistent style and make it easy to chain
together successive CASA reduction commands to generate a casapy command-script
programmatically; e.g.

`importUVFITS ->
Perform Clean on resulting MeasurementSet`

is implemented like so::

    ms = drivecasa.commands.import_uvfits(script, uvfits_path)
    dirty_maps = drivecasa.commands.clean(script, ms, niter=0, threshold_in_jy=1,
                                         other_clean_args=clean_args)


.. _CASA: http://casa.nrao.edu/
.. _virtualenv: http://www.virtualenv.org/

Rationale
---------
Newcomers to CASA_ should note that it is trivial to run
simple Python scripts within the casapy environment, or even to launch
casapy into a script directly from the command line, e.g.::

    casapy --nologger -c hello_world.py

While this mostly works fine from a command line or within a
shell script, things start to get messy if you want to run CASA functions
alongside routines from external Python libraries.


casapy uses its own bundled-and-modified copy of the Python interpreter[*],
so a first thought might be to try and install external libraries into the CASA
environment directly, and then run everything via the casapy interpreter.
Thanks to `recent efforts <https://github.com/radio-astro-tools/casa-python>`_,
this is now possible.
However it still breaks the virtualenv_ workflow,
and requires that your external Python modules are compatible with the
CASA-bundled version of Python.

Alternatively one can try to 'break-out' the casapy modules from the
CASA environment, but this also requires binary compatibility and some
monkeying around with embedded paths as detailed in
`this post from Peter Williams
<http://newton.cx/~peter/2014/02/casa-in-python-without-casapy/>`_.

At a pinch, you might be tempted to try dumping CASA command scripts to file
and then spawning a casapy instance via subprocess_. **Don't.** This was
how drive-casa got started, and I quickly ran into issues with casapy
filling the stdin / stdout pipe buffers and causing the whole process to
freeze up.

Which leads us to the drive-casa approach - emulate terminal interaction
with casapy via use of pexpect_. drive-casa can be installed
along with any other Python packages in the usual Python package fashion,
since we only interface with casapy indirectly via the command line.
The downside is that
data has to be written to file to transfer it between the standard Python script
and the casapy environment, but it brings some added benefits:

  Error handling
    CASA tasks do not, as far as I can tell, return useful values as standard
    (or even throw exceptions). Instead, since the over-riding assumption is that
    the package will be run in interactive mode,
    all information is written to stderr as part of the logging output, making it
    hard to programmatically verify if a task has completed sucessfully.
    drive-casa attempts to solve this by parsing the log output for 'SEVERE'
    warnings - the user may then choose to throw an exception when
    it is sensible to do so.

  Logging / reproducibility
    If scripting the reduction of large amounts of data in batches, it is
    often useful to record logging information along with the data output,
    both for purposes of debugging and data provenance.
    As far as I can tell, CASA does not provide an interface to control or
    redirect the logging output once the program has been instantiated.
    drive-casa can work-around this issue by simply restarting CASA with a fresh
    logging location specified for each dataset.


.. [*] This provides dedicated functionality, such as displaying a logging
    window and providing access to plotting tools - useful in interactive
    usage but undesirable from a scripting perspective.

.. _subprocess: https://docs.python.org/2/library/subprocess.html
.. _pexpect: http://pypi.python.org/pypi/pexpect/


Project status, licence and acknowledgement
-------------------------------------------
drive-casa is `BSD licensed`_.
The package is now in use by a few people
other than myself, and can reasonably be used 'in production'.
Any bug-fixes or interface changes should be accompanied by a version increment,
so you can be assured of stability by specifying the PyPI version.
I'd be interested to hear if others find it useful, and welcome
any bug reports or pull requests. Any major changes should be recorded in the
`change-log`_.

If you make use of drive-casa in work leading to a publication, I ask that
you cite `Staley and Anderson (2015)`_ and the relevant
`ASCL entry`_.

.. _BSD licensed: https://github.com/timstaley/drive-casa/blob/master/LICENCE.txt
.. _change-log: https://github.com/timstaley/drive-casa/blob/master/CHANGES.md
.. _Staley and Anderson (2015): http://labs.adsabs.harvard.edu/adsabs/abs/2015arXiv150508123S/
.. _ASCL entry: http://ascl.net/1504.006
 
Installation
------------
*Requirements*:

- A working installation of casapy.
- pexpect_
  (As listed in `requirements.txt`, installed automatically when using pip.) 
   
drive-casa is `pip` installable, simply run::

    pip install drive-casa

.. warning:: Multiprocessing bug with pexpect 3.3:

    During 2015, the default version of pexpect available on PyPI was 3.3.
    If you wish to use drive-casa in a parallel-processing context,
    you should beware of `this bug`_ which means
    pexpect 3.3 is broken under multiprocessing.
    Fortunately, both the older pexpect 2.4 and the latest pexpect `4.0.1`_
    seem to work fine.

.. _pip: http://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/
.. _this bug: https://github.com/pexpect/pexpect/issues/86
.. _4.0.1: https://pypi.python.org/pypi/pexpect/

Developer setup
---------------
Those wanting to modify the source will need a git checkout, 
followed by a git-submodule checkout to grab the test-data for the 
unittests. So a setup script might look like this::

    git clone git@github.com:timstaley/drive-casa.git
    cd drive-casa
    git submodule init
    git submodule update
    pip install -r requirements # (grab pexpect)
    cd tests
    nosetests -sv

Documentation
-------------
Reference documentation can be found at
http://drive-casa.readthedocs.org,
or generated directly from the repository using Sphinx_.


Usage
-----
Creating an instance of the :py:class:`drivecasa.interface.Casapy` class
will start up casapy in the background, awaiting instruction. Class init
arguments determine details such as where to find casapy, where to write
the casapy logfile, etc.
The :py:func:`drivecasa.interface.Casapy.run_script` and
:py:func:`drivecasa.interface.Casapy.run_script_from_file` commands can then
be used to send casapy a list of commands or a script to execute (through
use of the casapy execfile function). Logging output from the commands executed
is returned for inspection.

You are free to create the casapy scripts by any method you like, but a number
of convenience functions are provided that aim to make this process simpler
and more programmatic. These functions try to adhere to a consistent calling
signature, as detailed under :py:mod:`drivecasa.commands`.


.. _brief-example:

A Brief Example
---------------
Assuming you already have a uv-measurement dataset in uvFITS format,
basic usage might go something like this:

.. literalinclude:: examples/uvfits_to_dirty_map.py

After which, there should be a dirty map converted to FITS format waiting for 
you.

The `examples folder`_ also contains example scripts demonstrating how to simulate
and image a dataset from scratch.

.. _examples folder: https://github.com/timstaley/drive-casa/tree/master/documentation/source/examples

See also
--------
Note that drive-casa is designed as a fairly basic interface layer. If you're
putting together a substantial pipeline, you will probably want to built up
subroutines and data-structures around it, to keep your code manageable.
For one such example,
see chimenea_, a pipeline for automated processing of multi-epoch radio
observations.


.. _Sphinx: http://sphinx-doc.org/
.. _chimenea: https://github.com/timstaley/chimenea
