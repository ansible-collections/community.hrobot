#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Matthias Hurdebise <matthias_hurdebise@hotmail.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: storagebox_snapshot_info
short_description: Query the snapshots for a storage box
version_added: 2.4.0
author:
  - Matthias Hurdebise (@matthiashurdebise)
description:
  - Query the snapshots for a storage box.
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
- name: Query the snapshots
  community.hrobot.storagebox_snapshot_info:
    hetzner_user: foo
    hetzner_password: bar
    id: 123
  register: result

- name: Output data
  ansible.builtin.debug:
    msg: "Timestamp of the first snapshot : {{ result.snapshots[0].timestamp }}"
"""

RETURN = r"""
snapshots:
  description:
    - The storage box's info.
    - All date and time parameters are in UTC.
  returned: success
  type: list
  elements: dict
  contains:
    name:
      description:
        - The snapshot name.
      type: str
      sample: "2025-01-21T12-40-38"
      returned: success
    timestamp:
      description:
        - The timestamp of snapshot in UTC.
      type: str
      sample: "2025-01-21T13:40:38+00:00"
      returned: success
    size:
      description:
        - The Snapshot size in MB.
      type: int
      sample: 400
      returned: success
    filesystem_size:
      description:
        - The size of the Storage Box at creation time of the snapshot in MB.
      type: int
      sample: 12345
      returned: success
    automatic:
      description:
        - Whether the snapshot was created automatically.
      type: bool
      sample: false
      returned: success
    comment:
      description:
        - The comment for the snapshot.
      type: str
      sample: "This is a snapshot"
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
        storagebox_id=dict(type='int', required=True),
    )
    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    storagebox_id = module.params['storagebox_id']

    url = "{0}/storagebox/{1}/snapshot".format(BASE_URL, storagebox_id)
    result, error = fetch_url_json(module, url, accept_errors=['STORAGEBOX_NOT_FOUND'])
    if error:
        module.fail_json(msg='Storagebox with ID {0} does not exist'.format(storagebox_id))

    module.exit_json(
        changed=False,
        snapshots=[item['snapshot'] for item in result],
    )


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
