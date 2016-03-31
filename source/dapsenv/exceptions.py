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
from dapsenv.exitcodes import E_INVALID_CLI, E_NO_IMPLEMENTATION_FOUND, E_CONFIG_PROP_NOT_FOUND, \
                              E_CONFIG_FILE_PERMISSION_DENIED, E_CONFIG_FILE_NOT_CREATED
from dapsenv.logmanager import log

class DapsEnvException(Exception):
    pass

class InvalidCommandLineException(DapsEnvException):
    def __init__(self, message=""):
        if len(message):
            log.error(message)

        sys.exit(E_INVALID_CLI)

class InvalidActionException(DapsEnvException):
    def __init__(self, action):
        log.error("No implementation for '%s' found.", action)
        sys.exit(E_NO_IMPLEMENTATION_FOUND)

class InvalidConfigTypeException(DapsEnvException):
    pass

class ConfigPropertyNotFoundException(DapsEnvException):
    def __init__(self):
        sys.exit(E_CONFIG_PROP_NOT_FOUND)

class ConfigFilePermissionErrorException(DapsEnvException):
    def __init__(self, file_name):
        log.error("Could not access config file '%s'! Please check the permissions.", file_name)
        sys.exit(E_CONFIG_FILE_PERMISSION_DENIED)

class ConfigFileNotCreatedException(DapsEnvException):
    def __init__(self, file_name):
        log.error("Config file '%s' does not exist. Please generate it by using: 'dapsenv " \
              "config --generate --path %s", file_name, file_name)
        sys.exit(E_CONFIG_FILE_NOT_CREATED)
