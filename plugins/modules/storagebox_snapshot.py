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
version_added: 2.3.0
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
    support: full
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
      - Required when setting O(state) to V(absent), or when O(snapshot_comment) is specified.
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
---
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
  returned: success and O(state=present)
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
        "STORAGEBOX_NOT_FOUND": "Storagebox with ID {0} does not exist".format(storagebox_id),
        "SNAPSHOT_NOT_FOUND": "Snapshot with name {0} does not exist".format(snapshot_name),
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
        required_if=[["state", "absent", ["snapshot_name"]]],
        supports_check_mode=True
    )

    storagebox_id = module.params['storagebox_id']
    state = module.params['state']
    snapshot_name = module.params['snapshot_name']
    snapshot_comment = module.params['snapshot_comment']

    # Create snapshot
    if state == 'present' and not snapshot_name:
        if module.check_mode:
            module.exit_json(changed=True)
        snapshot = create_snapshot(module, storagebox_id)

        # Add the comment if provided
        if snapshot_comment is not None:
            update_snapshot_comment(
                module, storagebox_id, snapshot['name'], snapshot_comment)
            snapshot['comment'] = snapshot_comment

        module.exit_json(changed=True, snapshot=snapshot)

    # Update snapshot comment
    elif state == 'present' and snapshot_name:
        if snapshot_comment is None:
            module.fail_json(
                msg="snapshot_comment is required when updating a snapshot")

        snapshots = fetch_snapshots(
            module=module, storagebox_id=storagebox_id)
        snapshot = get_snapshot_by_name(snapshots, snapshot_name)
        if not snapshot:
            handle_errors(module, "SNAPSHOT_NOT_FOUND",
                          snapshot_name=snapshot_name)
        if snapshot_comment != snapshot['comment']:
            if not module.check_mode:
                update_snapshot_comment(
                    module, storagebox_id, snapshot_name, snapshot_comment)
            module.exit_json(changed=True, snapshot=snapshot)
        else:
            module.exit_json(changed=False, snapshot=snapshot)

    # Delete snapshot
    else:
        snapshots = fetch_snapshots(module=module, storagebox_id=storagebox_id)
        snapshot = get_snapshot_by_name(snapshots, snapshot_name)
        if snapshot:
            if not module.check_mode:
                delete_snapshot(module, storagebox_id, snapshot_name)
            module.exit_json(changed=True)
        else:
            module.exit_json(changed=False)


def delete_snapshot(module, storagebox_id, snapshot_name):
    url = "{0}/storagebox/{1}/snapshot/{2}".format(
        BASE_URL, storagebox_id, snapshot_name)
    fetch_url_json(module, url, method="DELETE", allow_empty_result=True)


def update_snapshot_comment(module, storagebox_id, snapshot_name, snapshot_comment):
    url = "{0}/storagebox/{1}/snapshot/{2}/comment".format(
        BASE_URL, storagebox_id, snapshot_name)
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    fetch_url_json(module, url, method="POST", data=urlencode(
        {"comment": snapshot_comment}), headers=headers, allow_empty_result=True)


def create_snapshot(module, storagebox_id):
    url = "{0}/storagebox/{1}/snapshot".format(BASE_URL, storagebox_id)
    result, error = fetch_url_json(module, url, method="POST", accept_errors=[
        "STORAGEBOX_NOT_FOUND", "SNAPSHOT_LIMIT_EXCEEDED"])
    if error:
        handle_errors(module, error, storagebox_id)
    return result['snapshot']


def get_snapshot_by_name(snapshots, name):
    for snapshot in snapshots:
        if snapshot['name'] == name:
            return snapshot
    return None


def fetch_snapshots(module, storagebox_id):
    url = "{0}/storagebox/{1}/snapshot".format(BASE_URL, storagebox_id)
    result, error = fetch_url_json(module, url, method="GET", accept_errors=[
        "STORAGEBOX_NOT_FOUND"])
    if error:
        handle_errors(module, error, storagebox_id)
    return [item['snapshot'] for item in result]


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
