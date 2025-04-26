#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: storagebox_info
short_description: Query information on one or more storage boxes
version_added: 2.1.0
author:
  - Felix Fontein (@felixfontein)
description:
  - Query information on one or more storage box.
extends_documentation_fragment:
  - community.hrobot.robot
  - community.hrobot.attributes
  - community.hrobot.attributes.actiongroup_robot
  - community.hrobot.attributes.idempotent_not_modify_state
  - community.hrobot.attributes.info_module

options:
  storagebox_id:
    description:
      - Limit result list to storage boxes with this ID.
    type: int
  linked_server_number:
    description:
      - Limit result list to storage boxes linked to the server with this number.
      - Ignored when O(storagebox_id) has been specified.
    type: int
  full_info:
    description:
      - Whether to provide full information for every storage box.
      - Setting this to V(true) requires one REST call per storage box, which is slow and reduces your rate limit. Use with care.
      - When O(storagebox_id) is specified, this option is always treated as having value V(true).
    type: bool
    default: false
"""

EXAMPLES = r"""
---
- name: Query a list of all storage boxes
  community.hrobot.storagebox_info:
    hetzner_user: foo
    hetzner_password: bar
  register: result

- name: Query a specific storage box
  community.hrobot.storagebox_info:
    hetzner_user: foo
    hetzner_password: bar
    storagebox_id: 23
  register: result

- name: Output data on specific storage box
  ansible.builtin.debug:
    msg: "Storage box name: {{ result.storageboxes[0].name }}"
"""

RETURN = r"""
storageboxes:
  description:
    - List of storage boxes matching the provided options.
  returned: success
  type: list
  elements: dict
  contains:
    id:
      description:
        - The storage box's ID.
      type: int
      sample: 123456
      returned: success
    login:
      description:
        - The storage box's login name.
      type: str
      sample: u12345
      returned: success
    name:
      description:
        - The storage box's name.
      type: str
      sample: Backup Server 1
      returned: success
    product:
      description:
        - The product name.
      type: str
      sample: BX60
      returned: success
    cancelled:
      description:
        - Whether the storage box has been cancelled.
        - The cancellation can still be un-done until RV(storageboxes[].paid_until) has been exceeded.
      type: bool
      sample: false
      returned: success
    locked:
      description:
        - Whether the IP is locked.
      type: bool
      sample: false
      returned: success
    location:
      description:
        - The storage box's location.
      type: str
      sample: FSN1
      returned: success
    linked_server:
      description:
        - The ID (server number) of the connected server, if available. Is V(null) otherwise.
      type: int
      sample: 123456
      returned: success
    paid_until:
      description:
        - The date until which the storage box has been paid for.
      type: str
      sample: "2015-10-23"
      returned: success
    disk_quota:
      description:
        - Total amount of MB available.
      type: int
      sample: 10240000
      returned: when O(full_info=true)
    disk_usage:
      description:
        - The amount of MB in use.
      type: int
      sample: 900
      returned: when O(full_info=true)
    disk_usage_data:
      description:
        - The amount of MB used by files.
      type: int
      sample: 500
      returned: when O(full_info=true)
    disk_usage_snapshots:
      description:
        - The amount of MB used by snapshots.
      type: int
      sample: 400
      returned: when O(full_info=true)
    webdav:
      description:
        - Whether WebDAV is active.
      type: bool
      sample: true
      returned: when O(full_info=true)
    samba:
      description:
        - Whether SAMBA is active.
      type: bool
      sample: true
      returned: when O(full_info=true)
    ssh:
      description:
        - Whether SSH is active.
      type: bool
      sample: true
      returned: when O(full_info=true)
    external_reachability:
      description:
        - Whether the storage box is reachable externally.
      type: bool
      sample: true
      returned: when O(full_info=true)
    zfs:
      description:
        - Shows whether the ZFS directory is visible.
      type: bool
      sample: false
      returned: when O(full_info=true)
    server:
      description:
        - The storage box's hostname.
      type: str
      sample: u12345.your-storagebox.de
      returned: when O(full_info=true)
    host_system:
      description:
        - Identifier of the storage box's host.
      type: str
      sample: FSN1-BX355
      returned: when O(full_info=true)
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode

from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    BASE_URL,
    ROBOT_DEFAULT_ARGUMENT_SPEC,
    fetch_url_json,
)


def main():
    argument_spec = dict(
        storagebox_id=dict(type='int'),
        linked_server_number=dict(type='int'),
        full_info=dict(type='bool', default=False),
    )
    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    storagebox_id = module.params['storagebox_id']
    linked_server_number = module.params['linked_server_number']
    full_info = module.params['full_info']

    storageboxes = []
    if storagebox_id is not None:
        storagebox_ids = [storagebox_id]
    else:
        url = "{0}/storagebox".format(BASE_URL)
        data = None
        headers = None
        if linked_server_number is not None:
            data = urlencode({
                "linked_server": linked_server_number,
            })
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
            }
        result, error = fetch_url_json(module, url, accept_errors=['STORAGEBOX_NOT_FOUND'], data=data)
        storagebox_ids = []
        if not error:
            # When filtering by linked_server, the result should be a dictionary
            if isinstance(result, dict):
                result = [result]
            for entry in result:
                if full_info:
                    storagebox_ids.append(entry['storagebox']['id'])
                else:
                    storageboxes.append(entry['storagebox'])

    for storagebox_id in storagebox_ids:
        url = "{0}/storagebox/{1}".format(BASE_URL, storagebox_id)
        result, error = fetch_url_json(module, url, accept_errors=['STORAGEBOX_NOT_FOUND'])
        if not error:
            storageboxes.append(result['storagebox'])

    module.exit_json(
        changed=False,
        storageboxes=storageboxes,
    )


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
