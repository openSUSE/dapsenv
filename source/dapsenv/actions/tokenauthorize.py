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

import dapsenv.token as token
import sys
from dapsenv.actions.action import Action
from dapsenv.daemonauth import DaemonAuth
from dapsenv.exceptions import InvalidTokenLengthException, InvalidTokenCharsException, \
                               TokenAlreadyAuthorizedException
from dapsenv.general import DAEMON_AUTH_PATH
from dapsenv.shellcolors import red

class Tokenauthorize(Action):
    def __init__(self):
        pass

    def execute(self, args):
        """@see Action.execute()
        """

        authfile = DaemonAuth(DAEMON_AUTH_PATH)

        for token in args["tokens"]:
            try:
                authfile.authorize(token)
                print("Successfully authorized token '{}'.".format(token))
            except (InvalidTokenLengthException, InvalidTokenCharsException):
                sys.stderr.write(red("Error: '{}' is not a valid token.\n".format(token)))
            except TokenAlreadyAuthorizedException:
                sys.stderr.write(red("Error: Token '{}' is already authorized.\n".format(token)))
