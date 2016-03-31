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

import re
from dapsenv.exceptions import InvalidConfigTypeException, ConfigFilePermissionErrorException, \
                               ConfigFileNotCreatedException
from os.path import expanduser, isfile

def get(prop, config_type="", config_path=""):
    """Returns the value of a property - should be used from other modules only!

    :param string prop: The requested property
    :param string config_type: The type of the config (global, user, own)
    :param string config_path: Sets the path for a configuration file (only required if "own"
                               is set in config_type)
    :return string: The value of the property or None
    """

    paths = []

    if len(config_type):
        paths = [get_config_path(config_type, config_path)]
    else:
        paths = [get_global_config_path(), get_user_config_path()]

    return get_property_value(prop, paths)

def set(prop, value, config_type="", config_path=""):
    """Sets the value of a property - should be used from other modules only!

    :param string prop: The requested property
    :param string value: The value to be set
    :param string config_type: The type of the config (global, user, own)
    :param string config_path: Sets the path for a configuration file (only required if "own"
                               is set in config_type)
    """

    path = get_config_path(config_type, config_path)
    set_property_value(prop, value, path)

def get_config_path(config_type, config_path=""):
    """Resolves a path for a config type

    :param string config_type: Sets the type of the wanted configuration file (global, user, own)
    :param string config_path: Will be returned if "own" is set as config_type
    :return string: a config path
    """

    if config_type == "own":
        return config_path
    elif config_type == "user":
        return get_user_config_path()
    elif config_type == "global":
        return get_global_config_path()

    raise InvalidConfigTypeException()

def get_global_config_path():
    """Returns the path of the global configuration file

    :return string: Path to the global configuration file
    """

    return "/etc/dapsenv/dapsenv.conf"

def get_user_config_path():
    """Returns the path of the user configuration file

    :return string: Path to the user configuration file
    """

    return "{}/.dapsenv/dapsenv.conf".format(expanduser("~"))

def get_property_value(prop, paths):
    """Returns the value of a property - should only be used internally!

    :param string prop: Name of the property
    :param list paths: The paths to look for configuration files
    :return string|None: The value of the given property or None if no appropriate property was
                         found
    """

    data = parse_config(paths)
    return data.get(prop)

def set_property_value(prop, value, path):
    """Sets a value for a property - should only be used internally!

    :param string prop: Name of the property
    :param string path: The path to the configuration file
    """

    if not isfile(path):
        ConfigFileNotCreatedException(path)

    content = ""
    added = False

    try:
        with open(path, "r+") as file_handle:
            for line in file_handle:
                # ignore lines starting with a hash (#) - comments
                if line[0] == "#":
                    content += line
                    continue

                # detect a property
                if len(line) and line[0] != "\n":
                    # cut property name from value
                    index = line.find("=")

                    # check if an equal sign was found
                    if index:
                        key = line[:index] # get property name
                        if key == prop:
                            content += "{}={}\n".format(key, value)
                            added = True
                            continue

                content += line

            # if the key does not exist, we append it to the end of the file
            if not added:
                # add a newline in front of the property name if the last character was not a newline
                if len(content) > 0 and content[-1] != "\n":
                    content += "\n"

                content += "{}={}".format(prop, value)

            # if the last character is a newline, remove it
            if content[-1] == "\n":
                content = content[:-1]

            # overwrite old config file content
            file_handle.seek(0)
            file_handle.truncate()
            file_handle.write(content)
    except PermissionError:
        raise ConfigFilePermissionErrorException(path)

def parse_config(paths):
    """Parses all given configuration files and returns their content

    :param list paths: A list of configuration files what should be parsed
    :return dict: All key-value pairs what were found in all of the given configuration files.
                  Duplicate entries will be overwritten by the next configuration file.
    """

    data = {}

    for path in paths:
        with open(path) as f:
            for line in f:
                # search for key=value pairs
                m = re.search("(?!#)(?P<key>[\w\d]+)\s*=\s*(?P<value>.*)", line)
                if m:
                    result = m.groupdict()
                    data[result["key"]] = result["value"]

    return data
