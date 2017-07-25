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

import os
import stat
import sys
from dapsenv.argparser import ArgParser
from dapsenv.exceptions import InvalidCommandLineException, InvalidActionException
from dapsenv.general import (HOME_DIR, LOG_DIR, TMP_DIR, BUILDS_DIR, TEMPLATE_PATH,
                             DAEMON_AUTH_PATH, CLIENT_TOKEN_PATH, TOKEN_LENGTH)
from dapsenv.logmanager import set_log_level
from dapsenv.utils import randomString, createdir
from importlib import import_module
from shutil import copyfile

import dapsenv.const
import logging
import logging.config

logging.getLogger().addHandler(logging.NullHandler())
logging.config.dictConfig(const.DEFAULT_LOGGING_DICT)
log = logging.getLogger(__package__)

def main(args=None):
    # todo better arg parsing
    log.setLevel(const.LOGLEVELS[2])
    # log.setLevel(LOGLEVELS.get(parsed_args["verbose"], logging.DEBUG))
    create_files()

    if not args:
        args = sys.argv[1:]

    # let's parse cli arguments with ArgParser()
    argparser = ArgParser(args)
    parsed_args = argparser.parse()

    # set log level
    set_log_level(parsed_args["verbose"])

    # if no sub-command/action was specified
    if not parsed_args["action"]:
        argparser.print_help()
        raise InvalidCommandLineException()

    # execute
    execute(parsed_args)


def create_files():
    """Creates all necessary files and directories
    """

    for d in (HOME_DIR, LOG_DIR, TMP_DIR, BUILDS_DIR):
        createdir(d)

    # files
    if not os.path.exists(CLIENT_TOKEN_PATH):
        with open(CLIENT_TOKEN_PATH, "w") as token_file:
            token_file.write(randomString(TOKEN_LENGTH))
            log.debug("%r created", CLIENT_TOKEN_PATH)

        os.chmod(CLIENT_TOKEN_PATH, stat.S_IREAD | stat.S_IWRITE)
        log.debug('chmod of %s', CLIENT_TOKEN_PATH)

    if not os.path.exists(DAEMON_AUTH_PATH):
        copyfile("{}/daemon-auth.xml".format(TEMPLATE_PATH), DAEMON_AUTH_PATH)
        log.debug("%r created", DAEMON_AUTH_PATH)
        os.chmod(DAEMON_AUTH_PATH, stat.S_IREAD | stat.S_IWRITE)
        log.debug('chmod of %s', DAEMON_AUTH_PATH)


def execute(args):
    # for the passed action/sub-command it's required to find the appropriate "Action Class". Each
    # sub-command has its own action class
    command = {
        "config": "config",
        "c": "config",
        "daemon": "daemon",
        "d": "daemon",
        "status": "status",
        "s": "status",
        "trigger-build": "triggerbuild",
        "tb": "triggerbuild",
        "project-list": "projectlist",
        "pl": "projectlist",
        "token": "token",
        "t": "token",
        "token-authorize": "tokenauthorize",
        "ta": "tokenauthorize",
        "token-deauthorize": "tokendeauthorize",
        "td": "tokendeauthorize",
        "view-log": "viewlog",
        "vl": "viewlog"
    }

    try:
        action = args["action"]
        result = command[action]
    except KeyError:
        raise InvalidActionException(action)

    try:
        class_name = result.title()
        module = import_module("dapsenv.actions.{}".format(action))

        # initialize class
        instance = getattr(module, class_name)()
        instance.execute(args)
    except ImportError:
        raise InvalidActionException(result)
