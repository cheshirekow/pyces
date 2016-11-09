#!/usr/bin/env python
# ARGCOMPLETE_OK
"""pyces daemon process"""

import argparse
import argcomplete
import codecs
import copy
import os
import sys
import time
import yaml

import pyces
from pyces.fmt_util import *

def make_dirs_if_needed(path):
    pardir = os.path.dirname(path)
    if not os.path.exists(pardir):
        os.makedirs(pardir)


def daemon_main(config, log_file):
    while True:
        time.sleep(1)


def start_daemon(config):
    # create the pid file in the safest way possible, with no race conditions
    pid_file_path = pyces.config_get(config, 'daemon.pid_file')
    log_file_path = pyces.config_get(config, 'daemon.log_file')
    make_dirs_if_needed(pid_file_path)
    make_dirs_if_needed(log_file_path)

    try:
        pid_fd = os.open(pid_file_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except OSError:
        fmt_err('There appears to be a pyces daemon already running, if you '
                'are sure that there is not, please remove the pid file at '
                '{}\n', pid_file_path).flush()
        return

    try:
        pid = os.fork()
    except OSError:
        fmt_err('Failed to fork off first of two children to start the'
                ' daemon\n').flush()
        return

    # parent process can close the pid file and continue on with whatever it
    # wanted to do
    if pid > 0:
        os.close(pid_fd)
        return

    pid_file = os.fdopen(pid_fd, 'w')
    log_file = codecs.getwriter('utf-8')(open(log_file_path, 'a'))

    # TODO(josh): implement signal handlers here?
    try:
        sid = os.setsid()
    except OSError:
        fmt_err('Failed to set new session id\n').flush()
        os.close(pid_file)
        os.remove(pid_file_path)
        sys.exit(1)

    # We shouldn't keep using these, but just in case
    sys.stdout = log_file
    sys.stderr = log_file

    # Fork off a second child that is not the session leader
    try:
        pid = os.fork()
    except OSError:
        fmt_file(log_file, "Failed to fork of second child.\n").flush()
        sys.exit(1)
        
    # parent process can die
    if pid > 0:
        sys.exit(0)

    # write and close the pid_file
    fmt_file(pid_file, '{}\n', os.getpid())
    pid_file.close()

    # close all open filedescriptors other than the log file
    # TODO(josh): figure out the correct way to get this
    # max_open_fds = os.sysconf('_SC_OPEN_MAX')
    # if max_open_fds == -1:
    #    max_open_fds = 100
    max_open_fds = 100

    for close_fd in xrange(max_open_fds):
        if close_fd == log_file.fileno():
            pass
        try:
            os.close(close_fd)
        except OSError:
            pass

    # now we can actually star the daemon
    # TODO(josh): not caught if signaled
    try:
        daemon_main(config, log_file)
    finally:
        log_file.flush()
        os.remove(pid_file_path)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-c', '--config-file', default=DEFCONFIG_PATH,
                      help='location of pyces global config file')
  argcomplete.autocomplete(parser)
  args = parser.parse_args()
  config = pyces.load_config(args.config_file)
  start_daemon(config)

if __name__ == '__main__':
  main()
