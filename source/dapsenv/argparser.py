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

import argparse
from dapsenv.general import __version__

class ArgParser:

    def __init__(self, args):
        self.args = args
        self.parser = argparse.ArgumentParser(
            description="A build environment to build documentations with DAPS."
        )
        self.cmdSubParser = self.parser.add_subparsers(
            dest="action",
            title="Available subcommands",
        )

        self.addGlobalOptions()
        self.addConfigCommand()

    def print_help(self):
        self.parser.print_help()

    def parse(self):
        return vars(self.parser.parse_args(args=self.args))

    def addGlobalOptions(self):
        self.parser.add_argument(
            "--version", action="version", help="Displays the current version of this program.",
            version="DAPS Build Environment Version {}".format(__version__)
        )

    def addConfigCommand(self):
        cmd = self.cmdSubParser.add_parser(
            "config", aliases=["c"], help="Modifying the configuration file"
        )

        config_group = cmd.add_mutually_exclusive_group(required=True)

        config_group.add_argument(
            "--global", "-g", action="store_true", help="Specifies to use the global " \
            "configuration which is stored in the configuration directory /etc."
        )

        config_group.add_argument(
            "--user", "-u", action="store_true", help="Specifies to use the user configuration " \
            "which is stored in the home directory of the current user."
        )

        cmd.add_argument(
            "--property", "-p", action="store", required=True,
            help="Specifies a property from the config file. If no value is set with --value, " \
            "only the current value of the property will be print on the command line."
        )

        cmd.add_argument(
            "--value", action="store", help="Sets a new value for a property."
        )
