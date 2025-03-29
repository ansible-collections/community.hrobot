#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: storagebox_snapshot
short_description: Create, update, or delete a snapshot of a storage box
author:
  - Matthias Hurdebise (@matthiashurdebise)
description:
  - Create, update comment, or delete a snapshot of a storage box.
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
    support: partial
    details:
      - This module is not idempotent when creating a snapshot.
options:
  storagebox_id:
    description:
      - The ID of the storage box to snapshot.
    type: int
    required: true
  snapshot_name:
    description:
      - The name of the snapshot to comment or delete.
      - The snapshot name is automatically generated and should not be specified when creating a snapshot.
      - Required when setting O(state) to V(absent)
      - Required when O(snapshot_comment) is specified
    type: str
  state:
    description:
      - The state of the snapshot.
    type: str
    default: present
    choices:
      - present
      - absent
  snapshot_comment:
    description:
      - The comment to set for the snapshot.
    type: str
"""

EXAMPLES = r"""
- name: Create a snapshot
  community.hrobot.storagebox_snapshot:
    storagebox_id: 12345
    # The snapshot name is automatically generated and should not be specified.

- name: Delete a snapshot
  community.hrobot.storagebox_snapshot:
    storagebox_id: 12345
    snapshot_name: "2025-01-21T12-40-38"
    state: absent

- name: Update snapshot comment
  community.hrobot.storagebox_snapshot:
    storagebox_id: 12345
    snapshot_name: "2025-01-21T12-40-38"
    snapshot_comment: "This is an updated comment"
"""

RETURN = r"""
snapshot:
  description:
    - The snapshot that was created.
  returned: success
  type: dict
  contains:
    name:
      description: The name of the snapshot.
      type: str
      sample: "2025-01-21T12-40-38"
    timestamp:
      description: Timestamp of snapshot in UTC
      type: str
      sample: "2025-01-21T12:40:38+00:00"
    size:
      description: The size of the snapshot in MB.
      type: int
      sample: 400
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode


from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    BASE_URL,
    ROBOT_DEFAULT_ARGUMENT_SPEC,
    fetch_url_json,
)


def handle_errors(module, error, storagebox_id=None, snapshot_name=None):
    error_messages = {
        "STORAGEBOX_NOT_FOUND": "Storagebox with ID {} does not exist".format(storagebox_id),
        "SNAPSHOT_NOT_FOUND": "Snapshot with name {} does not exist".format(snapshot_name),
        "SNAPSHOT_LIMIT_EXCEEDED": "Snapshot limit exceeded",
    }
    module.fail_json(msg=error_messages.get(error, error))


def main():
    argument_spec = dict(
        storagebox_id=dict(type='int', required=True),
        snapshot_name=dict(type='str'),
        state=dict(type='str', default="present",
                   choices=['present', 'absent']),
        snapshot_comment=dict(type='str')
    )

    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_by={"snapshot_comment": ["snapshot_name"]},
        required_if=[["state", "absent", ["snapshot_name"]]],
    )

    storagebox_id = module.params['storagebox_id']
    state = module.params['state']
    snapshot_name = module.params['snapshot_name']
    snapshot_comment = module.params['snapshot_comment']

    if state == 'present':
        if not snapshot_name:
            # Create snapshot
            url = "{}/storagebox/{}/snapshot".format(BASE_URL, storagebox_id)
            result, error = fetch_url_json(module, url, method="POST", accept_errors=[
                "STORAGEBOX_NOT_FOUND", "SNAPSHOT_LIMIT_EXCEEDED"])
            if error:
                handle_errors(module, error, storagebox_id)
            module.exit_json(changed=True, snapshot=result['snapshot'])
        else:
            if not snapshot_comment:
                module.fail_json(
                    msg="snapshot_comment is required when updating a snapshot")
            # Update snapshot comment
            url = "{}/storagebox/{}/snapshot/{}/comment".format(
                BASE_URL, storagebox_id, snapshot_name)
            headers = {"Content-type": "application/x-www-form-urlencoded"}
            dummy, error = fetch_url_json(module, url, method="POST", data=urlencode(
                {"comment": snapshot_comment}), headers=headers, accept_errors=["STORAGEBOX_NOT_FOUND", "SNAPSHOT_NOT_FOUND"], allow_empty_result=True)
            if error:
                handle_errors(module, error, storagebox_id, snapshot_name)
            module.exit_json(changed=True)

    elif state == 'absent':
        # Delete snapshot
        url = "{}/storagebox/{}/snapshot/{}".format(
            BASE_URL, storagebox_id, snapshot_name)
        dummy, error = fetch_url_json(module, url, method="DELETE", accept_errors=[
            "STORAGEBOX_NOT_FOUND", "SNAPSHOT_NOT_FOUND"], allow_empty_result=True)
        changed = not bool(error)
        module.exit_json(changed=changed)


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
