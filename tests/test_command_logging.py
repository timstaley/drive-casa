import unittest
from unittest import TestCase
import drivecasa
import os
import tempfile
from drivecasa import default_test_ouput_dir


class TestCommandLogging(TestCase):
    """
    Ensure that logging of commands works correctly.
    """
    def shortDescription(self):
        return None

    def test_command_logging(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            commands_logfile = tmpfile.name
            #Use the temporary file path, but delete the empty file first...
            os.remove(commands_logfile)
        casa = drivecasa.Casapy(commands_logfile=commands_logfile,
                                    echo_to_stdout=False)
        script = ['tasklist()']
        out, errors = casa.run_script(script)
        with open(commands_logfile) as f:
            commands_log = f.read()

        commands_logged = commands_log.split('\n')
        if not commands_logged[-1]:
            commands_logged.pop()
        self.assertEqual(commands_logged, script)
        # print "Command log", commands_log
        os.remove(commands_logfile)
