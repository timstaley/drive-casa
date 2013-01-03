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

def get_grouped_file_listings(listings):
    grp_names = list(set([i[drivecasa.keys.group_name] for i in listings.values()]))
    groups = {}
    for g_name in grp_names:
        grp = [i for i in listings.values() if i[drivecasa.keys.group_name] == g_name]
        groups[g_name] = grp
    return groups

def process_groups(groups, output_dir, casa_dir):
    for grp_name in sorted(groups.keys()):
            files = groups[grp_name]
            grp_dir = os.path.join(os.path.expanduser(output_dir),
                                   str(grp_name))
            for f in files:
                try:
                    logging.info('Processing observation: %s', f[drivecasa.keys.obs_name])
                    drivecasa.process_observation(f, grp_dir, casa_dir)
                except (ValueError, IOError):
                    logging.warn("Hit exception imaging target: " + f[Keys.obs_name])
                    continue
    return groups

def output_preamble_to_log(groups):
    logger.info("*************************")
    logger.info("Processing with casapy:")
    for key in sorted(groups.keys()):
        logger.info("%s:", key)
        for f in groups[key]:
            logger.info("\t %s", f[drivecasa.keys.obs_name])
        logger.info("--------------------------------")
    logger.info("*************************")

##=======================================================================
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
    print "Processing listings in:", listings_file
    listings = json.load(open(listings_file))
    groups = get_grouped_file_listings(listings)
    output_preamble_to_log(groups)
    updated_groups = process_groups(groups,
                          options.output_dir, options.casa_dir)
    sys.exit(0)

