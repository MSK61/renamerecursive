#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
renames a directory tree recursively

Usage: renRec.py -o OLDREGEX -n NEWNAME [-l] [-u] [-c RENCMD] FILE...
"""

############################################################
#
# Copyright 2011 Mohammed El-Afifi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# program:      recursive rename utility
#
# file:         renRec.py
#
# function:     complete program listing in this file
#
# description:  renames given files/directories recursively
#
# author:       Mohammed Safwat (MS)
#
# environment:  Komodo IDE, version 6.1.3, build 66534, python 2.6.6,
#               Fedora release 16 (Verne)
#
# notes:        This is a private program.
#
############################################################

import itertools
import os
from os import path
from os.path import join
import re
from re import sub
import subprocess
import sys
import optparse
# command-line option variables
# variables to receive case manipulation options
_LOWER_CASE_VAR = "handle_lower"
_UPPER_CASE_VAR = "handle_upper"
# variables to receive old and new name patterns
_OLD_REGEX_VAR = "old_name_regex"
_NEW_PAT_VAR = "new_name_pat"
_REN_CMD_VAR = "ren_cmd"  # rename command to use

def process_command_line(argv):
    """
    Return a 2-tuple: (settings object, args list).
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = optparse.OptionParser(
        "%prog -o OLDREGEX -n NEWNAME [-l] [-u] [-c RENCMD] FILE...",
        formatter=optparse.TitledHelpFormatter(width=78),
        add_help_option=None)

    # define options here:
    parser.add_option(      # rename command
        '-c', '--exec', dest=_REN_CMD_VAR,
        help='Use this command to rename.')
    parser.add_option(      # lower case handling
        '-l', '--lower-case', dest=_LOWER_CASE_VAR, action="store_true",
        help='Rename matching lower-case old names to lower-case new ones.')
    parser.add_option(      # new name pattern
        '-n', '--new-pattern', dest=_NEW_PAT_VAR,
        help='Use this pattern as the new name for files/directories to be '
        'renamed.')
    parser.add_option(      # old regular expression
        '-o', '--old-regex', dest=_OLD_REGEX_VAR,
        help='Rename files/directories matching this regular expression.')
    parser.add_option(      # upper case handling
        '-u', '--upper-case', dest=_UPPER_CASE_VAR, action="store_true",
        help='Rename matching upper-case old names to upper-case new ones.')
    parser.add_option(      # customized description; put --help last
        '-h', '--help', action='help',
        help='Show this help message and exit.')

    settings, args = parser.parse_args(argv)

    # check number of arguments, verify values:
    if not getattr(settings, _OLD_REGEX_VAR):
        parser.error("no old name regular expression specified!")

    if not getattr(settings, _NEW_PAT_VAR):
        parser.error("no new name pattern specified!")

    if not args:
        parser.error('program takes at least one file; none specified.')

    return settings, args

def main(argv=None):
    settings, args = process_command_line(argv)
    run(settings, args)
    return 0        # success


def run(settings, entries):
    """Rename the given entries recursively.

    `settings` are the options for processing entries.
    `entries` are the filesystem objects to rename.
    The function renames matching names from the given entries
    recursively to new names according to the given conversion criteria.

    """
    for cur_entry in entries:
        (_rename_tree if path.isdir(cur_entry) else _rename_obj)(
            cur_entry, settings)


def _rename_obj(obj_name, settings):
    """Rename the given object.

    `obj_name` is the object to rename.
    `settings` are the options for processing the object.
    The function renames the given object to a new name according to the
    given conversion criteria.

    """
    old_pat = getattr(settings, _OLD_REGEX_VAR)
    new_pat = getattr(settings, _NEW_PAT_VAR)
    dir_name, base_name = path.split(obj_name)
    new_name = sub(old_pat, new_pat, base_name)
    handle_lower = getattr(settings, _LOWER_CASE_VAR)
    handle_upper = getattr(settings, _UPPER_CASE_VAR)

    if new_name == base_name and (handle_lower or handle_upper):

        # Try detecting a unified case for the old name and substitue
        # accordingly with the same case of the new name.
        candid_name = sub(old_pat, new_pat, base_name, flags=re.IGNORECASE)

        if handle_lower:  # lower case
            if base_name.lower() == base_name:
                new_name = candid_name.lower()

        if new_name == base_name and handle_upper:  # upper case
            if base_name.upper() == base_name:
                new_name = candid_name.upper()

    new_name = join(dir_name, new_name)
    ren_cmd = getattr(settings, _REN_CMD_VAR)

    if ren_cmd:  # custom rename command specified
        subprocess.call([ren_cmd, obj_name, new_name])
    else:  # Use the built-in rename command.
        os.rename(obj_name, new_name)


def _rename_tree(dir_name, settings):
    """Rename the given directory recursively.

    `dir_name` is the directory to rename.
    `settings` are the options for processing the directory.
    The function renames the given directory recursively to a new name
    according to the given conversion criteria.

    """
    run(settings, itertools.imap(
        lambda entry: join(dir_name, entry), os.listdir(dir_name)))
    _rename_obj(dir_name, settings)


if __name__ == '__main__':
    status = main()
    sys.exit(status)
