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

import dapsenv.configmanager as configmanager
from dapsenv.actions.action import Action
from dapsenv.exceptions import ConfigPropertyNotFoundException, InvalidCommandLineException

class Config(Action):
    def __init__(self):
        pass

    def execute(self, args):
        """@see Action.execute()
        """

        self._args = args
        self._path = args["path"]

        # determine wished configuration type
        if self._args["global"]:
            self._configtype = "global"
        elif self._args["user"]:
            self._configtype = "user"
        elif self._args["own"]:
            self._configtype = "own"

        # check command line
        self._check_command_line()

        # check if the user either wants to modify the configuration or to just get the
        # value of a property
        if not args["value"]:
            self.get_property(self._args["property"])
        else:
            self.set_property(self._args["property"], self._args["value"])

    def get_property(self, prop):
        """Displays the value of the wanted property

        :param string prop: The name of the property
        """

        value = configmanager.get_prop(prop, self._configtype, self._path)
        if value:
            print(configmanager.get_prop(prop, self._configtype, self._path))
        else:
            raise ConfigPropertyNotFoundException()

    def set_property(self, prop, value):
        """Sets a property of a value

        :param string prop: The name of the property
        :param string value: The value to be set
        """

        configmanager.set_prop(prop, value, self._configtype, self._path)

    def _check_command_line(self):
        if self._configtype == "own" and not self._path:
            raise InvalidCommandLineException("The option --own requires also --path to be set.")
        elif not self._configtype == "own" and self._path:
            raise InvalidCommandLineException("Option --path is only required in combination " \
                "with --own.")
