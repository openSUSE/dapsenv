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

import asyncio
import dapsenv.configmanager as configmanager
import dapsenv.git as Git
import grp
import os
import pwd
import time
from dapsenv.actions.action import Action
from dapsenv.autobuildconfig import AutoBuildConfig
from dapsenv.docker import Container
from dapsenv.exceptions import AutoBuildConfigurationErrorException, UserNotInDockerGroupException
from dapsenv.general import DAEMON_DEFAULT_INTERVAL

class Daemon(Action):
    def __init__(self):
        pass

    def execute(self, args):
        """@see Action.execute()
        """

        self._noout = args["no_output"]

        # check requirements
        self.checkRequirements()

        # load auto build configuration file
        self.autoBuildConfig = self.loadAutoBuildConfig(
            configmanager.get_prop("daps_autobuild_config")
        )

        # load daemon settings
        self.loadDaemonSettings()

        # start daemon
        self.start()

    def start(self):
        """Starts the daemon
        """

        self._print("The daemon is now running.")

        self.check()

        while True:
            time.sleep(self._interval)
            self.check()

    def check(self):
        """Starts docker containers if a documentation got updated
        """

        self._print("\nChecking for updates in documentation repositories...")

        # check and refresh all repositories
        self._prepare_build_task()

        self._print("Next scheduled check: {}".format(time.ctime(time.time()+self._interval)))

    def _prepare_build_task(self):
        """Goes through all specified repositories and updates those
        """

        projects = self.autoBuildConfig.fetchProjects()
        for i in projects:
            if not "repo" in projects[i]:
                projects[i]["repo"] = Git.Repository(projects[i]["vcs_repodir"])

            commit = projects[i]["repo"].getLastCommitHash("master")

            # check if the last commit hash got changed
            if projects[i]["vcs_lastrev"] != commit:
                # update to the new commit hash
                projects[i]["vcs_lastrev"] = commit

                self._print("Project '{}' got updated. Starting build...".format(
                    projects[i]["project"]
                ))

                # start and prepare a container
                container = Container()
                container.spawn()
                container.prepare(projects[i]["vcs_repodir"])

                # building the documentation
                result = container.build_documentation("DC-suse-openstack-cloud-admin", ["html"])

                # kill and delete container from the registry
                container.kill()

    def _print(self, message):
        """Prints messages to the CLI
        """

        if not self._noout:
            print(message)

    def loadAutoBuildConfig(self, path):
        """Loads the auto build config file into memory and parses it

        :param string path: Specifies the path where the file is stored
        """

        if not path:
            raise AutoBuildConfigurationErrorException()

        return AutoBuildConfig(path)


    def loadDaemonSettings(self):
        """Loads the settings for the daemon
        """

        try:
            self._interval = int(configmanager.get_prop("daemon_check_interval"))
        except TypeError:
            self._interval = DAEMON_DEFAULT_INTERVAL

    def checkRequirements(self):
        """Check user requirements what are needed to run the daemon
        """

        user = pwd.getpwuid(os.getuid()).pw_name

        for group in grp.getgrall():
            if group.gr_name == "docker":
                if user in group.gr_mem:
                    return True

        raise UserNotInDockerGroupException()
