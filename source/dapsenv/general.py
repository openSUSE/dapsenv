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

from os import path

# specifies the current version of this program
__version__ = "1.0.0"

# the default pull interval for the daemon
DAEMON_DEFAULT_INTERVAL=300

# max docker containers default value
DAEMON_DEFAULT_MAX_CONTAINERS=15

# the directory where a repository should be copied in a container
CONTAINER_REPO_DIR="/tmp/build"

# the name of the docker image
CONTAINER_IMAGE="mschnitzer/dapsenv"

# user directory
USER_DIR="{}/.dapsenv".format(path.expanduser("~"))

# source directory of this python project
SOURCE_DIR=path.dirname(path.realpath(__file__))

# home directory
HOME_DIR="{}/.dapsenv".format(USER_DIR)

# error log directory
LOG_DIR="{}/.dapsenv/logs".format(USER_DIR)

# tmp directory
TMP_DIR="{}/.dapsenv/tmp".format(USER_DIR)

# tmp directory
BUILDS_DIR="{}/.dapsenv/builds".format(USER_DIR)

# templates location
TEMPLATE_PATH="{}/templates".format(SOURCE_DIR)

# daemon-auth.xml file location
DAEMON_AUTH_PATH="{}/daemon-auth.xml".format(USER_DIR)

# token file
CLIENT_TOKEN_PATH="{}/token".format(USER_DIR)

# api server default port
API_SERVER_DEFAULT_PORT=5555

# max token length
TOKEN_LENGTH=32
