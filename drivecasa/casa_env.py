"""Convenience routines for manipulating shell environments.

We generally grab the current shell env, then update paths with package specific
directories.

This is a nice way to ensure everything happens in its own sandbox,
without confusing interaction between conflicting variables.
"""
import os

def _append_to_path(env, path, extra_dir):
    """Deal nicely with empty path, minimise boilerplating."""
    env_dirs = env.get(path, '').split(':')
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

    `casa_topdir` should either contain the bin / lib directories containing CASA
    executables and libraries, or be set to None if casa is already available
    from the default environment.

    NB it's not a bad idea to always specify the casa dir anyway,
    so you don't have to rely on the environment paths being set up already.

    """
    casa_env = {}
    casa_env.update(os.environ)
    if casa_topdir is not None:
        _add_bin_lib_python(casa_env, casa_topdir)
    return casa_env
