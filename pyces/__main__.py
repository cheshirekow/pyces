#!/usr/bin/env python
# ARGCOMPLETE_OK
"""pyces user entry point"""

import argh
import argcomplete
import copy
import os
import sys
import yaml

import pyces
import pyces.daemon
from pyces.fmt_util import *


takes_config = argh.arg('-c', '--config-file', default=pyces.DEFCONFIG_PATH,
                        help='location of pyces global config file')


def defconfig(outpath='-'):
  """Print default config to file (or stdout)"""
  if outpath == '-':
    outfile = sys.stdout
  else:
    outdir = os.path.dirname(outpath)
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    outfile = open(outpath, 'w')

  yaml.dump(pyces.DEFAULT_CONFIG, outfile, width=80, indent=2,
            default_flow_style=False)


@takes_config
def execute(config_file=pyces.DEFCONFIG_PATH, source_dir='.'):
  """Execute a build"""
  config = pyces.load_config(config_file)
  pyces.daemon.start_daemon(config)
  pass


@takes_config
def shutdown(config_file=pyces.DEFCONFIG_PATH):
  """Shutdown the pyces global server."""
  config = pyces.load_config(config_file)
  pass


def main():
  parser = argh.ArghParser(description=__doc__)
  parser.add_commands([defconfig, execute, shutdown])
  argcomplete.autocomplete(parser)
  parser.dispatch()


if __name__ == '__main__':
  main()
