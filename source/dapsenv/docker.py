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
import shlex
import subprocess
import time
from collections import OrderedDict
from dapsenv.exceptions import ContainerNotSpawnedException, ContainerAlreadySpawnedException, \
                               ContainerPreparationMissingException, \
                               UnexpectedStderrOutputException, ContainerFileCreationFailed
from dapsenv.general import CONTAINER_REPO_DIR, CONTAINER_IMAGE, SOURCE_DIR, HOME_DIR
from random import randint

class Container:

    def __init__(self):
        self._spawned = False
        self._prepdone = False
        self._container_repopath = ""

    def spawn(self):
        """This function sets up a Docker container

        :return string: ID of the created Container
        """

        if self._spawned:
            raise ContainerAlreadySpawnedException()

        cmd = "docker run -t -d {} /bin/sh -c \"while true;do sleep 1;done\"".format(CONTAINER_IMAGE)

        with open("/dev/null", "w") as devnull:
            process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=devnull)

        self._spawned = True
        self._container_id = process.stdout.read().decode("utf-8")[:-1]

        return self._container_id

    def kill(self):
        """Kills the created container
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        with open("/dev/null", "w") as devnull:
            cmd = "docker rm -f {}".format(self.getContainerID())
            subprocess.Popen(shlex.split(cmd), stdout=devnull)

        self._spawned = False
        self._prepdone = False
        self._container_id = ""
        self._container_repopath = ""

    def getContainerID(self):
        """Returns the ID of this container

        :return string: Container ID
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        return self._container_id

    def getContainerRepoPath(self):
        """Returns the path to the repository inside the container

        :return String: The path
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        return self._container_repopath

    def prepare(self, repopath):
        """Prepares a container (copies the documentation repository into it)

        :param string repopath: Specifes the path, where the repository of the Documentation is
                                located
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        repodir = self._get_repodir(repopath)
        self._repodir = repodir
        self._prepdone = True
        self._container_repopath = "{}/{}".format(CONTAINER_REPO_DIR, repodir)

        self.execute("mkdir -p {}".format(CONTAINER_REPO_DIR))
        self.put(repopath, CONTAINER_REPO_DIR)
        self.put("{}/data/build.sh".format(SOURCE_DIR), "/tmp")
        self.put("{}/data/guidename.xsl".format(SOURCE_DIR), "/tmp")

        # a timing issue appears sometimes - that's why we need to make sure that the
        # file is really copied over before we go ahead
        count = 0
        while count < 10:
            if self.fileAvailable("/tmp/build.sh"):
                return
            else:
                count += 1
                time.sleep(1)

        raise ContainerPreparationMissingException(
            "/tmp/build.sh is not available inside the container."
        )

    def execute(self, command):
        """Executes a command inside a container

        :param string command: The command
        :return dict: With 'stdout' and 'stderr' as keys
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        cmd = "docker exec {} {}".format(self.getContainerID(), command)
        process = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        output = {
            "stdout": process.stdout.read().decode("utf-8"),
            "stderr": process.stderr.read().decode("utf-8")
        }

        return output

    def put(self, file_name, destination):
        """Puts a file or a directory into the container

        :param string file: The file/directory to put
        :param string destination: The destination inside the container
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        devnull = open("/dev/null", "w")

        cmd = "docker cp {} {}:{}".format(file_name, self.getContainerID(), destination)
        subprocess.Popen(shlex.split(cmd), stdout=devnull)

    def fetch(self, file_name, destination):
        """Fetches a file from the container

        :param string file: The file/directory in the docker container
        :param string destination: The destination where the file should be copied
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        devnull = open("/dev/null", "w")

        cmd = "docker cp {}:{} {}".format(self.getContainerID(), file_name, destination)
        subprocess.Popen(shlex.split(cmd), stdout=devnull)

    def fileAvailable(self, file_name):
        """Checks if a file is available inside the container

        :param string file_name: The path to look at
        :param bool: true = file exists | false = file does not exist
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        res = self.execute("stat {}".format(file_name))
        if not len(res["stderr"]):
            return True

        return False

    def fileCreate(self, file_name, content):
        """Creates a file inside the container

        :param string file_name: The file path
        :param string content: The content of the file
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        tmp_file_name = "container_file_creation_{}".format(randint(10000000,99999999))
        tmp_file_path = "{}/tmp/{}".format(HOME_DIR, tmp_file_name)

        # write tmp file
        with open(tmp_file_path, "w") as f:
            f.write(content)

        # copy file into the container
        self.put(tmp_file_path, file_name)

        # wait until the file was copied into the container
        count = 0
        while count < 10:
            if self.fileAvailable(file_name):
                break

            count += 1
            time.sleep(1)

        if count == 10:
            raise ContainerFileCreationFailed(file_name)

        # remove temporary file
        os.remove(tmp_file_path)

    def buildDocumentation(self, dc_file, formats):
        """Trys to build the documentation

        :param string dc_file: The name of the DC file
        :param list formats: A list of formats what should be built (like html, pdf etc.)
        :return OrderedDict: A dictionary with the build results
        """

        if not self._spawned:
            raise ContainerNotSpawnedException()

        if not self._prepdone:
            raise ContainerPreparationMissingException()

        results = OrderedDict()

        for index, f in enumerate(formats):
            start = int(time.time())

            cmd = "/tmp/build.sh {} {} {} {}".format(
                dc_file, f, self.getContainerRepoPath(), self._repodir
            )
            self.execute(cmd)

            cmd = "cat /tmp/build_status"
            status = self.execute(cmd)

            if status["stderr"]:
                raise UnexpectedStderrOutputException(cmd, status["stderr"])

            cmd = "cat /tmp/build_log"
            log = self.execute(cmd)

            if status["stderr"]:
                raise UnexpectedStderrOutputException(cmd, log["stderr"])

            if "success" in status["stdout"]:
                result = True
            else:
                result = False

            results[index] = {}
            results[index]["dc_file"] = dc_file
            results[index]["format"] = f
            results[index]["build_log"] = log["stdout"]
            results[index]["build_status"] = result
            results[index]["compile_time"] = int(time.time()) - start

        return results

    def _get_repodir(self, repopath):
        """Returns the directory name of a specified repository path

        :param string repopath: Path to the repository
        :return string: Directory name
        """

        if not len(repopath):
            return None

        if repopath[-1] == "/":
            repopath = repopath[:-1]

        repopath = repopath.split("/")
        return repopath[-1]
