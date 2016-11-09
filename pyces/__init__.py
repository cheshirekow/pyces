import copy
import os
import sys
import yaml


from pyces.fmt_util import *

class Path(str):
    "A callable string representing a directory path"

    def __call__(self, *args):
        return Path('/'.join([self] + list(args)))

DEFCONFIG_PATH = os.getenv('PYCES_CONFIG',
                           os.path.expanduser('~/.pyces/config.yaml'))

def get_default_config():
    work_root = Path(os.path.expanduser('~/.pyces'))
    daemon_dir = work_root('daemon')

    return {
        'daemon' : {
            'pid_file' : daemon_dir('pid'),
            'log_file' : daemon_dir('log')
        }
    }

def config_get(config_dict, keypath):
    "get a dictionary value by decimated keypath"
    if isinstance(keypath, str):
        keypath = keypath.split('.')

    value = config_dict
    for key in keypath:
        value = value.get(key, {})

    return value

def config_set(config_dict, keypath, value):
    "get a dictionary value by decimated keypath"

    if isinstance(keypath, str):
        keypath = keypath.split('.')

    parent = config_dict
    for key in keypath[:-1]:
        if key not in parent:
            parent[key] = dict()
        parent = parent[key]
    
    parent[keypath[-1]] = value

 
DEFAULT_CONFIG = get_default_config()


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
