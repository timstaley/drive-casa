import logging
import os
import sys
import json
import itertools
import pexpect
import tempfile
import drivecasa.utils
from drivecasa.casa_env import casapy_env
logger = logging.getLogger(__name__)

# Historical note:
# A simple subprocess was looking like a good option for a while;
# especially as we only want the stderr, usually.
# However, a long running script creates enough output to fill the pipe,
# which then blocks. So we would need to do a non-blocking read on the
# pipe to get the process to continue. At this point, I decided to switch
# to pexpect - at least this way we can reuse the casapy process once
# instantiated.


class Casapy(object):
    def __init__(self,
                 casa_logfile=None,
                 casa_dir=None,
                 working_dir='/tmp/drivecasa',
                 timeout=600,
                 log2term=True,
                 echo_to_stdout=False,
                 ):
        """
        **Args:**
          - casa_logfile: Valid options are: 'None' (use default behaviour of a
            logfile named 'casapy-<date>-<time>.log' in the working directory),
            'False' (do not log to file), or a string containing a path to save
            the log to. The path may either be absolute, or specified relative
            to the current working directory of the python process.
          - working_dir: The directory casapy will be run from. Casapy drops
            various bits of cruft into this directory, such as ipython log snippets,
            '.last' parameter storage files, etc. You can specify this if the
            default isn't suitable (though it should be fine on Linux).
          - timeout: The maximum time allowed for a single casapy command to
            complete, in seconds. It may be necessary to increase this for e.g.
            very complex 'clean' routines.
          - log2term: Use the 'log2term' casapy flag to tell it to echo regular
            log messages to the subprocess casa_out pipe. This provides a running
            commentary on the process, the contents of which are returned by this
            function. Usually only error messages are logged here.
          - echo_to_stdout: Echo all Casapy output to the python stdout.
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

        if log2term:
            cmd.append('--log2term')

        logger.debug("Starting casa with flags: ")
        logger.debug(" ".join(cmd))
        self.child = pexpect.spawn('casapy',
                     cmd,
                     cwd=working_dir,
                     env=casapy_env(casa_dir),
                     timeout=timeout)
        if echo_to_stdout:
            self.child.logfile_read = sys.stdout
        self.prompt = r'CASA <[0-9]+>:'
        self.child.expect(self.prompt)

    def run_script(self, script, raise_on_severe=True):
        """
        **Args:**
          - script: A list of commands to execute.
          - raise_on_severe: Raise a ``RuntimeError`` if SEVERE messages are
            encountered in the logging output. Set to ``False`` if you want to
            attempt to continue execution anyway. (Often useful if e.g.
            running a basic ``import_uvfits`` (with ``overwrite=False``),
            since if the data has been imported once before then casapy will
            raise an error to tell you it will not overwrite the pre-existing
            files.


        **Returns:**
            (casa_out, errors)

            I.e. a tuple of the contents of the
            subprocess casa_out pipe, followed by a list of 'SEVERE' error messages.
            Both the casa_out string and error list are empty if everything went well
            (although see also the ``log2term`` arg).
            If return_stdout is True, then the tuple is prefaced by the stdout pipe
            contents, giving::


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
        for line in script:
            # Casapy gets upset when you feed it a long command
            # The output gets filled with backspace characters as it reformats,
            # which is a PITA to parse.
            # So instead, we dump the command in a tempfile, and tell casa to
            # exec it. Oh, the perversity!
            with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
                tmpfile_path = tmpfile.name
                tmpfile.write(line + '\n')
            self.child.sendline("execfile('{}')".format(tmpfile_path))
            self.child.expect(self.prompt)
            os.remove(tmpfile_path)
            out_lines = self.child.before.split('\r\n')
            # Skip the first line: 'execfile(blah)'
            casa_out.extend(out_lines[1:])
            for line in out_lines:
                tokens = line.split('\t', 2)
                if len(tokens) >= 2 and tokens[1] == 'SEVERE':
                    errors.append(line)
            if errors and raise_on_severe:
                error_str = '\n'.join(errors)
                raise RuntimeError(
                           "Casapy encountered a 'SEVERE' level problem running the "
                           "following command: \n"
                           "*********\n" + "\n".join(line) + "\n*********\n" +
                           "Errors are as follows:\n" + error_str)
        return casa_out, errors
