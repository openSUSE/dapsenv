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
import random
import string

import logging
log = logging.getLogger(__name__)

def randomString(len):
    """Generates a random string

    :param int len: Length of the generated string
    :return string: Random string
    """
    return "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(len))

def createdir(path):
    """Make a new directory if it do not exist

    :param string path: path to new directory
    """
    if not os.path.exists(path):
        os.makedirs(path)
        log.debug("%r created", path)
    else:
        log.debug("%r already exists", path)
