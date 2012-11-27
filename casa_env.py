"""Defines various shell environments for use with subprocess.

We generally grab the current shell env, then update paths with package specific
directorys.

This is a nice way to ensure everything happens in its own sandbox,
without confusing interaction between conflicting variables.
"""
import os

def _append_to_path(env, path, extra_dir):
    """Deal nicely with empty path, minimise boilerplating."""
    env_dirs = env[path].split(':')
    env_dirs.append(extra_dir)
    env[path] = ':'.join(env_dirs)

def _add_bin_lib_python(env, package_group_dir, include_python=True):
    """Add the bin, lib, (and optionally python-packages) subdirs of
    `package_group_dir` to the relevant environment paths."""
    _append_to_path(env, "PATH", os.path.join(package_group_dir, 'bin'))
    _append_to_path(env, 'LD_LIBRARY_PATH',
                    os.path.join(package_group_dir, 'lib'))
    if include_python:
        _append_to_path(env, 'PYTHONPATH',
                        os.path.join(package_group_dir, 'python-packages'))

def casapy_env(casa_topdir):
    """Returns an environment dictionary configured for CASA execution.
        
    `casa_topdir` should contain the bin / lib directories containing CASA
    executables and libraries.
    
    """
    casa_env = {}
    casa_env.update(os.environ)
    _add_bin_lib_python(casa_env, casa_topdir)
    return casa_env