# Changelog
-------------

## r0.7.6 (2016-11-22)
- Add examples scripts for data-simulation
- Rearrange string-formatting subroutines into their own module.

## r0.7.5 (2016-05-27)
- Catch more syntax errors when executing CASA scripts.
- Add subroutine-calls for various CASA data-simulation commands.
- Restructure docs a bit.

## r0.7.4 (2016-05-06)
- Add `timeout` argument to `run_script`.
Allows for use of differing timeout values for particular long-running
commands.

## r0.7.3 (2016-05-04) 
- Switch to [versioneer][] for release tagging
- Update interface class for CASA 4.5+ compatibility.
- Various minor fixes to unit-tests.

[versioneer]: https://github.com/warner/python-versioneer

## r0.7.1 (2016-05-04)
- Update `install_requires` to install pexpect version 4, (version 4 fixes
the multiprocessing issues which previously meant we were pinned to 
pexpect==2.4).

## r0.7.0 (2015-10-15)
- Add ['mstransform'][] command, modify 'Clean' to accept multiple visibilities.
(Thanks to Dave Pallot, [PR #6][]).
- Tidy up `output_path` generation for 'concat' and other functions.
- Start recording changelog
- Updated citation reference in docs.


['mstransform']: http://www.eso.org/~scastro/ALMA/casa/MST/MSTransformDocs/MSTransformDocs.html
[PR #6]: https://github.com/timstaley/drive-casa/pull/6
