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
from dapsenv.exceptions import ConfigPropertyNotFoundException

class Config(Action):
    def __init__(self):
        pass

    def execute(self, args):
        """@see Action.execute()
        """

        # determine wished configuration type
        if args["global"]:
            self.configtype = "global"
        elif args["user"]:
            self.configtype = "user"

        # check if the user either wants to modify the configuration or to just get the
        # value of a property
        if not args["value"]:
            self.get_property(args["property"])
        else:
            self.set_property(args["property"], args["value"])

    def get_property(self, prop):
        """Displays the value of the wanted property

        :param string prop: The name of the property
        """

        value = configmanager.get(prop, self.configtype)
        if value:
            print(configmanager.get(prop, self.configtype))
        else:
            raise ConfigPropertyNotFoundException()

    def set_property(self, prop, value):
        pass
