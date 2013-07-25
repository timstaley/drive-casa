==========
drive-casa
==========
A python package for scripting the NRAO CASA_ ``casapy`` pipeline routines.

Rationale
---------
Casapy actually makes use of an altered version of IPython to provide a 
user interface, and all of the routines available are in fact python functions.
This means it *is* possible to write python scripts and run them from within
``casapy`` itself. However, there are some compelling reasons not to do so:

  - Casapy comes bundled with its very own python installation - version 2.6, 
    in fact. This is getting pretty long in the tooth, and means that any code
    written elsewhere for 2.7 will need to be compatibility tested for 2.6, 
    before running it under casapy.
  - The 'bundled installation' model also means that setting up a virtualenv
    to run casa scripts in is effectively impossible, thus preventing well 
    encapsulated and reproducible data-reduction environments.
  - Casapy tasks do not, AFAICT, return any useful values. Rather, since the 
    over-riding assumption is that the package will be run in interactive mode,
    all information is written to stderr as part of the logging output. While 
    this cannot generally be solved by an external scripting interface, the
    specific issue of errors can be handled more gracefully - by parsing the 
    log output for 'SEVERE' warnings we can choose to throw an exception when
    it is sensible to do so.
  - If scripting the reduction of large amounts of data in batches, it is 
    often useful to record logging information along with the data output,
    both for purposes of debugging and data provenance. AFAICT, Casapy does
    not provide an interface to control or redirect the logging output once
    the program has been instantiated. We can sidestep this problem by 
    interfacing via the command line, and simply restarting casapy with a fresh
    logging location specified for each dataset.  


Status
------
This package is still in the alpha stage - as such the interface may change in 
a backward incompatible manner without warning. However, if you think it could
be of use to you, drop me a line.

 
Installation
------------

*Requirements*:
 - A working installation of ``casapy`` (naturally).
 - `pexpect <http://pypi.python.org/pypi/pexpect/>`_ 
   (Installed automatically as part of the python setup.) 
   
From the command line (preferably within a virtualenv):: 

 git clone git://github.com/timstaley/drive-casa.git
 cd drive-casa
 pip install numpy #Workaround for buggy scipy/numpy combined install.
 pip install .


.. _CASA: http://casa.nrao.edu/
