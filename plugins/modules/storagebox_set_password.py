#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: storagebox_set_password
short_description: (Re)set the password for a storage box
version_added: 2.1.0
author:
  - Matthias Hurdebise (@matthiashurdebise)
description:
  - (Re)set the password for a storage box.
extends_documentation_fragment:
  - community.hrobot.robot
  - community.hrobot.attributes
  - community.hrobot.attributes.actiongroup_robot

attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
  idempotent:
    support: none
    details:
      - This module performs an action on every invocation.

options:
  id:
    description:
      - The ID of the storage box to modify.
    type: int
    required: true
  password:
    description:
      - The new password for the storage box.
      - If not provided, a random password will be created by the Robot API
        and returned as RV(password).
    type: str
"""

EXAMPLES = r"""
- name: Set the password
  community.hrobot.storagebox_set_password:
    id: 123
    password: "newpassword"

- name: Set a random password
  community.hrobot.storagebox_set_password:
    id: 123
  register: result

- name: Output new password
  ansible.builtin.debug:
    msg: "New password: {{ result.password }}"
"""

RETURN = r"""
password:
  description:
    - The new password for the storage box.
    - Note that if the password has been provided as O(password), Ansible will censor this return value to something
      like C(VALUE_SPECIFIED_IN_NO_LOG_PARAMETER).
  returned: success
  type: str
  sample: "newpassword"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode

from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    BASE_URL,
    ROBOT_DEFAULT_ARGUMENT_SPEC,
    fetch_url_json,
)


def main():
    argument_spect = dict(
        id=dict(type="int", required=True),
        password=dict(type="str", no_log=True),
    )
    argument_spect.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    module = AnsibleModule(argument_spect, supports_check_mode=False)

    id = module.params["id"]
    password = module.params.get("password")

    url = "{0}/storagebox/{1}/password".format(BASE_URL, id)
    accepted_errors = ["STORAGEBOX_NOT_FOUND", "STORAGEBOX_INVALID_PASSWORD"]

    if password:
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        result, error = fetch_url_json(
            module, url, method="POST", accept_errors=accepted_errors, data=urlencode({"password": password}), headers=headers)
    else:
        result, error = fetch_url_json(
            module, url, method="POST", accept_errors=accepted_errors)

    if error == 'STORAGEBOX_NOT_FOUND':
        module.fail_json(
            msg='Storage Box with ID {0} not found'.format(id))

    if error == 'STORAGEBOX_INVALID_PASSWORD':
        module.fail_json(
            msg="The chosen password has been considered insecure or does not comply with Hetzner's password guideline")

    module.exit_json(changed=True, password=result["password"])


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
