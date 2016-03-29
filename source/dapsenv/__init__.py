#
# Copyright (c) 2016 SUSE Linux GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact SUSE LLC.
#
# To contact SUSE about this file by physical or electronic mail,
# you may find current contact information at www.suse.com

import sys
from dapsenv.argparser import ArgParser
from dapsenv.exceptions import *
from importlib import import_module

def main(args=None):
    if not args:
        args = sys.argv[1:]

    # let's parse cli arguments with ArgParser()
    argparser = ArgParser(args)
    parsed_args = argparser.parse()

    # if no sub-command/action was specified
    if not parsed_args["action"]:
        argparser.print_help()
        raise InvalidCommandLineException()

    # execute related stuff for the sub-command
    execute(parsed_args["action"])

def execute(action):
    # for the passed action/sub-command it's required to find the appropriate "Action Class". Each
    # sub-command has its own action class
    try:
        class_name = action.title()
        module = import_module("dapsenv.actions.{}".format(action))

        # initialize class
        instance = getattr(module, class_name)()
        instance.execute()
    except (ImportError, AttributeError):
        raise InvalidActionException(action)
