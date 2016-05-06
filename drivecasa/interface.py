import logging
import os
import sys
import pexpect
import tempfile
import drivecasa.utils
from drivecasa.casa_env import casapy_env
import drivecasa.commands.subroutines as subroutines
logger = logging.getLogger(__name__)

# Historical note:
# A simple subprocess was looking like a good option for a while;
# especially as we only want the stderr, usually.
# However, a long running script creates enough output to fill the pipe,
# which then blocks. So we would need to do a non-blocking read on the
# pipe to get the process to continue. At this point, I decided to switch
# to pexpect - at least this way we can reuse the casapy process once
# instantiated.

default_casa_dir = os.environ.get('CASA_DIR', None)

class Casapy(object):
    """
    Handles the interface with casapy.

    Simply instantiate, then use member function 'run_script' to pass
    valid casapy commands (i.e. python function calls) to casapy.

    .. note::

        Imported into the root of the ``drivecasa`` package to provide convenient
        instantiation, e.g::

            casa = drivecasa.Casapy()
            casa.run_script(['tasklist'])


    """
    def __init__(self,
                 casa_logfile=None,
                 commands_logfile=None,
                 casa_dir=default_casa_dir,
                 working_dir='/tmp/drivecasa',
                 timeout=600,
                 log2term=True,
                 echo_to_stdout=False,
                 ):
        """
        Initialise a casapy instance.

        Args:
            casa_logfile: Valid options are:

                - `None` (uses default behaviour of a logfile named
                  `casapy-<date>-<time>.log` in the working directory),
                - `False` (do not log to file), or
                - string containing a path to save the log to. The path may
                  either be absolute, or specified relative to the current
                  working directory of the calling python process.
            commands_logfile: Path of logfile to record all commands passed to
                this casapy instance via scripts. If left to default of
                ``None``, so such record is kept.
            casa_dir: Path to the top-level directory containing the CASA
                package. If the default of ``None`` is used, then drive-casa
                will attempt to call casapy from the default $PATH, as imported
                from ``os.environ``.
            working_dir: The directory casapy will be run from. Casapy drops
                various bits of cruft into this directory, such as ipython log snippets,
                '.last' parameter storage files, etc. You can specify this if the
                default of `/tmp/drivecasa` isn't suitable, though it should be fine
                on Linux.
            timeout: The maximum time allowed for a single casapy command to
                complete, in seconds. It may be necessary to increase this e.g. for
                very complex `clean` routines.
            log2term: Use the 'log2term' casapy flag to tell it to echo regular
                log messages to the subprocess casa_out pipe. This provides a running
                commentary on the process, the contents of which are returned by this
                function. Usually only error messages are logged here.
            echo_to_stdout: Echo all Casapy output to the python stdout.
                Effectively, this gives a running commentary on what's happening,
                at the price of cluttering your working terminal. As an alternative,
                it is recommended to open a separate terminal and ``tail -f`` the
                casa_logfile.
        """
        drivecasa.utils.ensure_dir(working_dir)
        # NB It would make sense to switch off ipython, ('noipython' flag)
        # but doing so breaks stuff! I suspect this may be a bug.

        # NB also nologger/nogui: I suspect these are undocumented synonyms,
        # but who knows.
        cmd = [  # "casapy",
                '--nologger',
                '--nogui',
                '--colors=NoColor',
    #             '--noipython',
                ]

        if casa_logfile is not None:
            if casa_logfile is False:
                cmd.append('--nologfile')
            else:
                # Make path absolute, in case user has specified a relative path
                # (Might expect relative to python execution, but will *get*
                # path relative to casa working dir).
                cmd.extend(['--logfile', os.path.abspath(casa_logfile) ])

        self.commands_logfile_handle = None
        if commands_logfile is not None:
            try:
                if os.path.isfile(commands_logfile):
                    raise ValueError("Will not overwrite a logfile, "
                                 "try including a timestamp in the filename.")
                self.commands_logfile_handle = open(commands_logfile, 'w')
            except Exception as e:
                logger.error("Hit an exception trying to open a commands logfile "
                             "at " + commands_logfile)
                raise


        if log2term:
            cmd.append('--log2term')

        logger.debug("Starting casa with flags: ")
        logger.debug(" ".join(cmd))

        if casa_dir is None:
            casapy_cmd = 'casa'  # Assume it's in $PATH
        else:
            casapy_cmd = os.path.join(casa_dir, 'bin', 'casa')

        failed_casapy_spawns = 0
        self.child=None
        while failed_casapy_spawns < 3:
            try:
                self.child = pexpect.spawn(casapy_cmd,
                             cmd,
                             cwd=working_dir,
                             env=casapy_env(casa_dir),
                             timeout=timeout)
                if echo_to_stdout:
                    self.child.logfile_read = sys.stdout
                self.prompt = r'CASA <[0-9]+>:'
                self.child.expect(self.prompt, timeout=60)
                break
            except pexpect.TIMEOUT:
                #Try again
                failed_casapy_spawns += 1
                logger.warning("%s CASA spawning timeouts occurred." %
                                failed_casapy_spawns)
                self.child=None
        if self.child is None:
            raise RuntimeError("Could not spawn CASA instance")
        self.load_subroutines()


    def run_script(self, script, raise_on_severe=True, timeout=-1):
        """
        Run the commands listed in `script`.

        Args:
            script: A list of commands to execute.
             (One command per list element.)
            raise_on_severe: Raise a ``RuntimeError`` if SEVERE messages are
              encountered in the logging output. Set to ``False`` if you want to
              attempt to continue execution anyway (e.g. if you want to ignore
              errors caused by trying to re-import UVFITs data when the outputs
              are pre-existing from a previous run).
            timeout: If `-1` (the default, use the class default timeout).
                Otherwise, specifies timeout in seconds for this command.
                `None` implies no timeout (wait indefinitely).


        Returns:
            Tuple ``(casa_out, errors)``
                Where ``casa_out`` is a line-by-line list containing the contents
                of the casapy terminal output, and ``errors`` is a line-by-line
                list of 'SEVERE' error messages.


        """
    #     casa = subprocess.Popen(cmd,
    #                         cwd=working_dir,
    #                         env=casapy_env(casa_dir),
    #                         stdout=subprocess.PIPE,
    #                         casa_out=subprocess.PIPE,
    #                         )

        casa_out = []
        errors = []
        logger.debug("Running casa script:")
        logger.debug("*************")
        logger.debug('\n' + '\n'.join([l for l in script]))
        logger.debug("*************")
        for cmd in script:
            # Casapy gets upset when you feed it a long command
            # The output gets filled with backspace characters as it reformats,
            # which is a PITA to parse.
            # So instead, we dump the command in a tempfile, and tell casa to
            # exec it. Oh, the perversity!
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile_path = tmpfile.name
                tmpfile.write(cmd + '\n')
            try:
                if self.commands_logfile_handle is not None:
                    self.commands_logfile_handle.write(cmd+'\n')
                    self.commands_logfile_handle.flush()
                line_out, line_err = self.run_script_from_file(tmpfile_path,
                                                       raise_on_severe,
                                                       command_pre_logged=True,
                                                       timeout=timeout)
            except RuntimeError as e:
                raise RuntimeError(
                       "Casapy encountered a 'SEVERE' level problem running the "
                       "command "+cmd+"\n"
                       "Error message is as follows:\n" +
                       e.message)
            casa_out.extend(line_out)
            errors.extend(line_err)

            os.remove(tmpfile_path)
            out_lines = self.child.before.split('\r\n')
        return casa_out, errors

    def run_script_from_file(self, path_to_scriptfile, raise_on_severe=True,
                             command_pre_logged=False,
                             timeout=-1):
        """
         Run the script at given path.

        Args:
            path_to_scriptfile: Can be relative or absolute, since we apply
              abspath conversion before passing to casapy.
            raise_on_severe: Raise a ``RuntimeError`` if SEVERE messages are
              encountered in the logging output. Set to ``False`` if you want to
              attempt to continue execution anyway (e.g. if you want to ignore
              errors caused by trying to re-import UVFITs data when the outputs
              are pre-existing from a previous run).
            timeout: If `-1` (the default, use the class default timeout).
                Otherwise, specifies timeout in seconds for this command.
                `None` implies no timeout (wait indefinitely).


        Returns:
            Tuple ``(casa_out, errors)``
                Where ``casa_out`` is a line-by-line list containing the contents
                of the casapy terminal output, and ``errors`` is a line-by-line
                list of 'SEVERE' error messages.
        """

        errors_from_file = []
        casa_out_from_file = []

        exec_cmd = "execfile('{}')".format(os.path.abspath(path_to_scriptfile))
        if not command_pre_logged and self.commands_logfile_handle is not None:
            self.commands_logfile_handle.write(exec_cmd+'\n')
            self.commands_logfile_handle.flush()
        self.child.sendline(exec_cmd)
        self.child.expect(self.prompt,timeout=timeout)
        out_lines = self.child.before.split('\r\n')
        # Skip the first line: 'execfile(blah)'
        casa_out_from_file.extend(out_lines[1:])
        for line in out_lines:
            tokens = line.split('\t', 2)
            if ( len(tokens) >= 2) and (tokens[1] == 'SEVERE'):
                errors_from_file.append(line)
        if errors_from_file and raise_on_severe:
            error_str = '\n'.join(errors_from_file)
            raise RuntimeError(
                   "Casapy encountered a 'SEVERE' level problem running the "
                   "script at "+path_to_scriptfile+": \n"
                   "*********\n" +
                   "\n".join(line) +
                   "\n*********\n" +
                   "Errors are as follows:\n" +
                   error_str)
        return casa_out_from_file, errors_from_file

    def load_subroutines(self):
        for subdef in (subroutines.def_load_antennalist,):
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile_path = tmpfile.name
                tmpfile.write(subdef + '\n')
            self.run_script_from_file(tmpfile_path, command_pre_logged=True)
