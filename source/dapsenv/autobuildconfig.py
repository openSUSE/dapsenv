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
from collections import OrderedDict
from dapsenv.exceptions import AutoBuildConfigSyntaxErrorException, AutoBuildConfigNotFound
from lxml import etree
from lxml.etree import XMLSyntaxError

class AutoBuildConfig:

	def __init__(self, path):
		"""Initializes the AutoBuildConfig class

		:param string path: The path to the auto build config file
		"""

		self._dcfiles_pattern = re.compile("DC\-[a-zA-Z\-_]+")

		self._path = path
		self.parse()

	def parse(self):
		"""Parses the given auto build config file
		"""

		try:
			self._tree = etree.parse(self._path)
		except XMLSyntaxError as e:
			raise AutoBuildConfigSyntaxErrorException(self._path, e)
		except IOError:
			raise AutoBuildConfigNotFound(self._path)

	def fetchProjects(self):
		"""returns all 'set' elements as a well formed structure

		:return OrderedDict: a structure with all projects and their details
		"""

		data = OrderedDict()
		projects = self._tree.findall("set")
		
		for index, project in enumerate(projects):
			project_name = project.attrib["id"]
			dc_files = project.find("dcfiles").text
			vcs_data = project.find("vcs")

			data[index] = {}
			data[index]["project"] = project_name
			data[index]["dc_files"] = self._parse_dc_files(dc_files)
			data[index]["vcs"] = vcs_data.attrib["type"]
			data[index]["vcs_branch"] = vcs_data.attrib["branch"]
			data[index]["vcs_repodir"] = vcs_data.find("checkout").text
			data[index]["vcs_lastrev"] = vcs_data.find("lastrev").text

		return data

	def _parse_dc_files(self, dc_files):
		"""Remove all trash characters from the 'dcfiles' element

		:return list: A list with all DC files
		"""

		return self._dcfiles_pattern.findall(dc_files)
