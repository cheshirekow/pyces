#!/usr/bin/env python
# ARGCOMPLETE_OK
"""pyces user entry point"""

import argh
import argcomplete
import copy
import os
import sys
import yaml


class FmtWrapper(object):

  def __init__(self, fileobj):
    self.fileobj = fileobj

  def __call__(self, fmt, *args, **kwargs):
    self.fileobj.write(fmt.format(*args, **kwargs))
    return self

  def flush(self):
    self.fileobj.flush()


def fmt_str(fmt, *args, **kwargs):
  return fmt.format(*args, **kwargs)


def fmt_out(fmt, *args, **kwargs):
  return FmtWrapper(sys.stdout)(fmt, *args, **kwargs)


def fmt_err(fmt, *args, **kwargs):
  return FmtWrapper(sys.stderr)(fmt, *args, **kwargs)


def fmt_file(fileobj, fmt, *args, **kwargs):
  return FmtWrapper(fileobj)(fmt, *args, **kwargs)


def fmt_raise(ex_class, fmt, *args, **kwargs):
  raise ex_class(fmt.format(*args, **kwargs))


def fmt_assert(assertion, fmt, *args, **kwargs):
  assert assertion, fmt.format(*args, **kwargs)


DEFCONFIG_PATH = os.getenv('PYCES_CONFIG',
                           os.path.expanduser('~/.pyces/config.yaml'))

takes_config = argh.arg('-c', '--config-file', default=DEFCONFIG_PATH,
                        help='location of pyces global config file')

DEFAULT_CONFIG = {
    'option_a': True,
    'option_b': False
}


def merge_config(primary, overrides):
  for key, value in overrides.iteritems():
    if key not in primary:
      fmt_err('WARNING: ignoring config override {}, which is not a '
              'config value\n', key).flush()
      continue
    if isinstance(primary[key], dict):
      if isinstance(overrides[key], dict):
        merge_config(primary[key], overrides[dict])
      else:
        fmt_err("WARNING: can't override config section {} with "
                "non-section\n", key).flush()
        continue
    else:
      try:
        primary[key] = type(primary[key])(value)
      except ValueError:
        fmt_err("WARNING: can't override config key {} of type "
                "{} with type {}\n", key, type(primary[key]),
                type(overrides[key])).flush()


def load_config(config_path):
  config = copy.deepcopy(DEFAULT_CONFIG)
  try:
    with open(config_path, 'r') as infile:
      override = yaml.load(infile)
      return merge_config(config, override)

  except IOError:
    fmt_err('Failed to open config file {}, using defaults\n',
            config_path).flush()
    return config
  except yaml.YAMLError as exc:
    if hasattr(exc, 'problem_mark'):
      mark = exc.problem_mark
      fmt_err('Parse error at {}:{}[{}]', config_path, mark.line + 1,
              mark.column + 1)
    else:
      fmt_err('Failed to parse {}\n', config_path)
    return config


def defconfig(outpath='-'):
  """Print default config to file (or stdout)"""
  if outpath == '-':
    outfile = sys.stdout
  else:
    outdir = os.path.dirname(outpath)
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    outfile = open(outpath, 'w')

  yaml.dump(DEFAULT_CONFIG, outfile, width=80, indent=2,
            default_flow_style=False)


@takes_config
def execute(config_file=DEFCONFIG_PATH, source_dir='.'):
  """Execute a build"""
  config = load_config(config_file)
  pass


@takes_config
def shutdown(config_file=DEFCONFIG_PATH):
  """Shutdown the pyces global server."""
  config = load_config(config_file)
  pass


def main():
  parser = argh.ArghParser(description=__doc__)
  parser.add_commands([defconfig, execute, shutdown])
  argcomplete.autocomplete(parser)
  parser.dispatch()


if __name__ == '__main__':
  main()
