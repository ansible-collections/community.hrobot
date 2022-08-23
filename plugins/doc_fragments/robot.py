# -*- coding: utf-8 -*-

# Copyright (c) 2019 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = r'''
options:
  hetzner_user:
    description: The username for the Robot webservice user.
    type: str
    required: true
  hetzner_password:
    description: The password for the Robot webservice user.
    type: str
    required: true
'''
