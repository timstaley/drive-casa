#!/usr/bin/python
import optparse
import os
import sys
import logging
import json
import itertools
import subprocess

import drivecasa

def handle_args():
    """
    Default values are defined here.
    """
    default_output_dir = os.path.expanduser("~/ami_results")
    default_casa_dir = os.path.expanduser('/opt/soft/builds/casapy-33.0.16856-002-64b')
    usage = """usage: %prog [options] datasets_to_process.json\n"""
    parser = optparse.OptionParser(usage)

    parser.add_option("-o", "--output-dir", default=default_output_dir,
                      help="Path to output directory (default is : " +
                            default_output_dir + ")")

    parser.add_option("--casa-dir", default=default_casa_dir,
                   help="Path to CASA directory, default: " + default_casa_dir)

    options, args = parser.parse_args()
    options.output_dir = os.path.expanduser(options.output_dir)
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    print "Reducing files listed in:", args[0]
    return options, args[0]


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s',
                    filemode='w',
                    filename="drive-casa.log",
                    level=logging.DEBUG)
    logger = logging.getLogger()
    log_stdout = logging.StreamHandler(sys.stdout)
    log_stdout.setLevel(logging.INFO)
    logger.addHandler(log_stdout)
    options, listings_file = handle_args()
    print "Opening:", listings_file
    listings = json.load(open(listings_file))
    updated_listings = drivecasa.process_data_listing(listings,
                          options.output_dir, options.casa_dir)
    sys.exit(0)

