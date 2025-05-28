#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Victor LEFEBVRE <dev@vic1707.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: storagebox_subaccount_info
short_description: Query the subaccounts for a storage box
version_added: 2.4.0
author:
  - Victor LEFEBVRE (@vic1707)
description:
  - Query the subaccounts for a storage box.
extends_documentation_fragment:
  - community.hrobot.robot
  - community.hrobot.attributes
  - community.hrobot.attributes.actiongroup_robot
  - community.hrobot.attributes.idempotent_not_modify_state
  - community.hrobot.attributes.info_module

options:
  storagebox_id:
    description:
      - The ID of the storage box to query.
    type: int
    required: true
"""

EXAMPLES = r"""
---
- name: Query the subaccounts
  community.hrobot.storagebox_subaccount_info:
    hetzner_user: foo
    hetzner_password: bar
    storage_box_id: 123
  register: result

- name: Output data
  ansible.builtin.debug:
    msg: "Username of the first subaccount: {{ result.subaccounts[0].username }}"
"""

RETURN = r"""
subaccounts:
  description:
    - The storage box's info.
    - All date and time parameters are in UTC.
  returned: success
  type: list
  elements: dict
  contains:
    username:
      description:
        - Username of the sub-account.
      type: str
      sample: "u2342-sub1"
      returned: success
    accountid:
      description:
        - Username of the main user.
      type: str
      sample: "u2342"
      returned: success
    server:
      description:
        - Server on which the sub-account resides.
      type: str
      sample: "sb1234.your-storagebox.de"
      returned: success
    homedirectory:
      description:
        - Homedirectory of the sub-account.
      type: str
      sample: "/home/u2342-sub1"
      returned: success
    samba:
      description:
        - Status of Samba support.
      type: bool
      sample: true
      returned: success
    ssh:
      description:
        - Status of SSH support.
      type: bool
      sample: true
      returned: success
    external_reachability:
      description:
        - Status of external reachability.
      type: bool
      sample: false
      returned: success
    webdav:
      description:
        - Status of WebDAV support.
      type: bool
      sample: true
      returned: success
    readonly:
      description:
        - Indicates if the sub-account is in readonly mode.
      type: bool
      sample: false
      returned: success
    createtime:
      description:
        - Timestamp when the sub-account was created.
      type: str
      sample: "2023-08-25T14:23:05Z"
      returned: success
    comment:
      description:
        - Custom comment for the sub-account.
      type: str
      sample: "This is a subaccount"
      returned: success
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    BASE_URL,
    ROBOT_DEFAULT_ARGUMENT_SPEC,
    fetch_url_json,
)


def main():
    argument_spec = dict(
        storagebox_id=dict(type="int", required=True),
    )
    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    storagebox_id = module.params["storagebox_id"]

    url = "{0}/storagebox/{1}/subaccount".format(BASE_URL, storagebox_id)
    result, error = fetch_url_json(module, url, accept_errors=["STORAGEBOX_NOT_FOUND"])
    if error:
        module.fail_json(
            msg="Storagebox with ID {0} does not exist".format(storagebox_id)
        )

    module.exit_json(
        changed=False,
        subaccounts=[item["subaccount"] for item in result],
    )


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
