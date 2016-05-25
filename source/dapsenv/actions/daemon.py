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
import copy
import dapsenv.configmanager as configmanager
import grp
import json
import os
import pwd
import sys
import threading
import time
import websockets
from dapsenv.actions.action import Action
from dapsenv.autobuildconfig import AutoBuildConfig
from dapsenv.docker import Container
from dapsenv.exceptions import AutoBuildConfigurationErrorException, \
                               UserNotInDockerGroupException, GitInvalidRepoException
from dapsenv.exitcodes import E_INVALID_GIT_REPO
from dapsenv.general import DAEMON_DEFAULT_INTERVAL, HOME_DIR, DAEMON_DEFAULT_MAX_CONTAINERS, \
                            API_SERVER_DEFAULT_PORT, LOG_DIR
from dapsenv.ircbot import IRCBot
from dapsenv.logmanager import log
from multiprocessing import Queue

class Daemon(Action):
    def __init__(self):
        pass

    def execute(self, args):
        """@see Action.execute()
        """

        self._useirc = args["use_irc"]
        self._noout = args["no_output"]
        self._debug = args["debug"]
        self._irc_config = {}
        self._ircbot = None

        # create locks for thread-safe communications
        self._irclock = threading.Lock()
        self._daemon_info_lock = threading.Lock()

        # check requirements
        self.checkRequirements()

        # load auto build configuration file
        self._autoBuildConfigFile = configmanager.get_prop("daps_autobuild_config")
        self.autoBuildConfig = self.loadAutoBuildConfig(
            self._autoBuildConfigFile
        )

        # fetch all projects
        try:
            self.projects = self.autoBuildConfig.fetchProjects()
        except GitInvalidRepoException as e:
            log.error("Configuration error in auto build config '%s'! %s", \
                self._autoBuildConfigFile, e.message)
            sys.exit(E_INVALID_GIT_REPO)

        # load daemon settings
        self.loadDaemonSettings()

        # load irc bot config
        self.loadIRCBotConfig()

        # prepare data object
        self._prepareDataObject()

        # start IRC bot
        if self._useirc:
            self._start_ircbot()

        # start api server
        self._api_server_start()

        # start daemon
        self.start()

    def _start_ircbot(self):
        thread = threading.Thread(target=self._thread_ircbot)
        thread.start()

    def _thread_ircbot(self):
        # initialize bot
        self._ircbot = IRCBot(
            self._irc_config["irc_server"],
            self._irc_config["irc_server_port"],
            self._irc_config["irc_channel"],
            self._irc_config["irc_bot_nickname"],
            self._irc_config["irc_bot_username"]
        )

        self._ircbot.setDaemon(self)
        self._ircbot.start()

    @asyncio.coroutine
    def _api_server_runtime(self, websocket, path):
        """This coroutine will be created for each new client what connects to the API server

        :param websockets.server.WebSocketServerProtocol websocket: Object for communicating with
                                                                    the current client
        :param string path: The path where the client want to go to
        """

        while True:
            # wait until the client sends data to the API server
            try:
                data = yield from websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                return

            try:
                # parse the sent data as json
                data = json.loads(data)

                # check for correct data packets
                if not "id" in data:
                    yield from websocket.close()
                    return
                else:
                    # accessing thread-safe daemon information
                    self._daemon_info_lock.acquire()
                    daemon_info = self._daemon_info.copy()
                    self._daemon_info_lock.release()

                    # receive daemon status
                    if data["id"] == 1:
                        # answer
                        yield from websocket.send(json.dumps(
                            {
                                "id": data["id"],
                                "running_builds": daemon_info["running_builds"]
                            }
                        ))
                    else:
                        # close if an invalid packet was received
                        yield from websocket.close()
                        return
            except ValueError:
                yield from websocket.close()
                return

    def _api_server_thread(self):
        """Spawns the API server
        """

        # set event loop handler
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # configure websocket server
        start_server = websockets.serve(self._api_server_runtime, "0.0.0.0", self._api_server_port)

        # event loop settings
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def _api_server_start(self):
        """Starts an API server in a new thread if configured
        """

        if self._api_server == "true":
            # spawn API server thread
            thread = threading.Thread(target=self._api_server_thread)
            thread.start()
        elif not self._api_server == "false":
            log.warn("Invalid option specified for 'api_server' in config file! Valid options: " \
                "true/false")

    def start(self):
        """Starts the daemon
        """

        if not self._debug:
            self._print("The daemon is now running.")
        else:
            self._print("The daemon is now running in the debug mode.")

        # prepare queue
        self._jobs = Queue()

        # start thread which is required to handle incoming jobs
        thread = threading.Thread(target=self._jobManager)
        thread.start()

        # run check
        self.check()

        while True:
            time.sleep(self._interval)
            self.check()

    def _jobManager(self):
        while True:
            # get all running builds
            self._daemon_info_lock.acquire()
            running_builds = self._daemon_info["running_builds"]
            self._daemon_info_lock.release()

            # search for new jobs in queue
            if not self._jobs.empty():
                while not self._jobs.empty():
                    if running_builds < self._max_containers:
                        data = self._jobs.get()

                        # create thread
                        thread = threading.Thread(
                            target=self._process,
                            args=(copy.deepcopy(data["project"]), data["dc_file"][:])
                        )

                        # start thread
                        thread.start()
                        
                        # update amount of running builds
                        self._daemon_info_lock.acquire()
                        self._daemon_info["running_builds"] += 1
                        self._daemon_info_lock.release()
                    else:
                        break

            time.sleep(1)

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

        for i in self.projects:
            # pull new commits into repository
            self.projects[i]["repo"].pull(self.projects[i]["vcs_branch"], force=True)

            # fetch current commit hash from branch
            commit = self.projects[i]["repo"].getLastCommitHash(self.projects[i]["vcs_branch"])

            # check if the last commit hash got changed
            if self.projects[i]["vcs_lastrev"] != commit:
                # update to the new commit hash
                self.projects[i]["vcs_lastrev"] = commit[:]

                # start and prepare a container in a new thread
                for dc_file in self.projects[i]["dc_files"]:
                    self._jobs.put({
                        "project": copy.deepcopy(self.projects[i]),
                        "dc_file": dc_file[:],
                        "commit": commit
                    })

    def _process(self, project_info, dc_file):
        """Thread function to start containers and build documentations

        :param dict project_info: A dictionary with information about that project
        :param string dc_file: DC what should get built
        """

        # create container
        container = Container()
        container.spawn()
        container.prepare(project_info["vcs_repodir"])

        # specify build formats
        build_formats = ["html", "single_html", "pdf"]

        for f in build_formats:
            # building the documentation
            result = container.buildDocumentation(dc_file, f)

            archive = result["archive_name"]
            del result["archive_name"]

            # parse the documentation info
            product = json.loads(container.execute("cat /tmp/doc_info.json")["stdout"])

            # add new information to result dict
            result.update(product)

            # if debug mode is enabled, add some additional information to the
            # build_info.json file
            if self._debug:
                result["container_id"] = container.getContainerID()
            else:
                # remove the daps command from the result dictionary, if debug mode
                # is disabled
                del result["dapscmd"]
    
            if result["build_status"]:
                # generate a build info file for the documentation archive
                container.fileCreate("/tmp/build_info.json", json.dumps(result))

                # add build info file to documentation archive
                container.execute("tar -C /tmp --append --file={} build_info.json".format(archive))

                # compress tar archive
                container.execute("gzip {}".format(archive))

                # copy compiled documentation into the builds/ directory of the user
                file_name = "{}_{}_{}.tar.gz".format(int(time.time()), dc_file[3:], f.replace("_", "-"))
                container.fetch("{}.gz".format(archive), "{}/builds/{}".format(
                    HOME_DIR, file_name
                ))

                self._irclock.acquire()

                if self._ircbot and self._irc_config["irc_inform_build_success"]:
                    self._ircbot.sendChannelMessage("A new build has been finished! " \
                        "DC-File: {}, Format: {}, Output-Archive: {}".format(
                            result["dc_file"],
                            result["format"],
                            file_name
                        )
                    )

                self._irclock.release()
            else:
                error_log_path = "{}/build_fail_{}_{}_{}.log".format(
                    LOG_DIR,
                    result["dc_file"],
                    result["format"],
                    int(time.time())
                )

                with open(error_log_path, "w+") as f:
                    f.write(result["build_log"])

                self._irclock.acquire()

                if self._ircbot and self._irc_config["irc_inform_build_fail"]:
                    self._ircbot.sendChannelMessage("A build has failed! " \
                        "DC-File: {}, Format: {}, Error-Log: {}".format(
                            result["dc_file"],
                            result["format"],
                            error_log_path
                        )
                    )

                self._irclock.release()

        # update amount of running builds
        self._daemon_info_lock.acquire()
        self._daemon_info["running_builds"] -= 1
        self._daemon_info_lock.release()

        # kill and delete container from the registry
        if not self._debug:
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

        self._current_builds = 0

        # daemon_check_interval
        try:
            self._interval = int(configmanager.get_prop("daemon_check_interval"))
        except TypeError:
            self._interval = DAEMON_DEFAULT_INTERVAL

        # daemon_max_containers
        try:
            self._max_containers = int(configmanager.get_prop("daemon_max_containers"))
        except TypeError:
            self._max_containers = DAEMON_DEFAULT_MAX_CONTAINERS

        # api_server
        self._api_server = configmanager.get_prop("api_server")

        # api_server_port
        try:
            self._api_server_port = int(configmanager.get_prop("api_server_port"))
        except TypeError:
            self._api_server_port = API_SERVER_DEFAULT_PORT

    def checkRequirements(self):
        """Check user requirements what are needed to run the daemon
        """

        user = pwd.getpwuid(os.getuid()).pw_name

        for group in grp.getgrall():
            if group.gr_name == "docker":
                if user in group.gr_mem:
                    return True

        raise UserNotInDockerGroupException()

    def _prepareDataObject(self):
        """This prepares the data object what contains information about running builds
        and some other statistics
        """

        self._daemon_info = {
            "running_builds": 0
        }

    def getStatus(self):
        self._daemon_info_lock.acquire()
        daemon_info = self._daemon_info.copy()
        self._daemon_info_lock.release()

        return daemon_info

    def loadIRCBotConfig(self):
        self._irc_config["irc_server"] = configmanager.get_prop("irc_server")
        self._irc_config["irc_server_port"] = int(configmanager.get_prop("irc_server_port"))
        self._irc_config["irc_channel"] = "#{}".format(configmanager.get_prop("irc_channel"))
        self._irc_config["irc_bot_nickname"] = configmanager.get_prop("irc_bot_nickname")
        self._irc_config["irc_bot_username"] = configmanager.get_prop("irc_bot_username")
        self._irc_config["irc_inform_build_success"] = True if \
            configmanager.get_prop("irc_inform_build_success") == "true" else False
        self._irc_config["irc_inform_build_fail"] = True if \
            configmanager.get_prop("irc_inform_build_fail") == "true" else False