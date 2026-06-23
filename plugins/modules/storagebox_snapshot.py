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
  - community.hrobot.api._robot_compat_shim_deprecation  # must come before api and robot
  - community.hrobot.api
  - community.hrobot.robot
  - community.hrobot.attributes
  - community.hrobot.attributes._actiongroup_robot_and_api_deprecation  # must come before the other two!
  - community.hrobot.attributes.actiongroup_api
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
  hetzner_token:
    version_added: 2.5.0
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
    - The snapshot that was created or updated.
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

from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    ROBOT_DEFAULT_ARGUMENT_SPEC,
    _ROBOT_DEFAULT_ARGUMENT_SPEC_COMPAT_DEPRECATED,
)

from ansible_collections.community.hrobot.plugins.module_utils.api import (
    API_BASE_URL,
    API_DEFAULT_ARGUMENT_SPEC,
    _API_DEFAULT_ARGUMENT_SPEC_COMPAT,
    ApplyActionError,
    api_apply_action,
    api_fetch_url_json,
)

try:
    from urllib.parse import urlencode
except ImportError:
    # Python 2.x fallback:
    from urllib import urlencode


def extract_legacy(snapshot):
    return {
        'id': snapshot['id'],
        'name': snapshot['name'],
        'comment': snapshot['description'],
        'timestamp': snapshot['created'],
        'size': snapshot['stats']['size'] // (1024 * 1024),
        'filesystem_size': snapshot['stats']['size_filesystem'] // (1024 * 1024),
    }


def main():
    argument_spec = dict(
        storagebox_id=dict(type='int', required=True),
        snapshot_name=dict(type='str'),
        state=dict(type='str', default="present",
                   choices=['present', 'absent']),
        snapshot_comment=dict(type='str')
    )
    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    argument_spec.update(_ROBOT_DEFAULT_ARGUMENT_SPEC_COMPAT_DEPRECATED)
    argument_spec.update(API_DEFAULT_ARGUMENT_SPEC)
    argument_spec.update(_API_DEFAULT_ARGUMENT_SPEC_COMPAT)

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[["state", "absent", ["snapshot_name"]]],
        supports_check_mode=True
    )

    storagebox_id = module.params['storagebox_id']
    state = module.params['state']
    snapshot_name = module.params['snapshot_name']
    snapshot_comment = module.params['snapshot_comment']

    if module.params["hetzner_user"] is not None:
        module.deprecate(
            "The hetzner_token parameter will be required from community.hrobot 3.0.0 on.",
            collection_name="community.hrobot",
            version="3.0.0",
        )
        module.warn("The old storagebox API has been disabled by Hetzner. The supporting code has been removed.")
        module.fail_json(msg="Storagebox with ID {0} does not exist".format(storagebox_id))

    # Create snapshot
    if state == 'present' and not snapshot_name:
        if module.check_mode:
            module.exit_json(changed=True)
        action_url = "{0}/v1/storage_boxes/{1}/snapshots".format(API_BASE_URL, storagebox_id)
        action = {}
        if snapshot_comment:
            action["description"] = snapshot_comment
        try:
            extracted_ids, error = api_apply_action(
                module,
                action_url,
                action,
                lambda action_id: "{0}/v1/storage_boxes/actions/{1}".format(API_BASE_URL, action_id),
                check_done_delay=1,
                check_done_timeout=120,
                accept_errors=["not_found"],
            )
        except ApplyActionError as exc:
            module.fail_json(msg='Error while creating snapshot: {0}'.format(exc))

        if error == "not_found":
            module.fail_json(msg="Storagebox with ID {0} does not exist".format(storagebox_id))

        new_snapshot_id = extracted_ids["storage_box_snapshot"]
        # Retrieve created snapshot
        url = "{0}/v1/storage_boxes/{1}/snapshots/{2}".format(API_BASE_URL, storagebox_id, new_snapshot_id)
        snapshot = api_fetch_url_json(module, url, method='GET')[0]["snapshot"]

        module.exit_json(changed=True, snapshot=extract_legacy(snapshot))

    # Update snapshot comment
    elif state == 'present' and snapshot_name:
        if snapshot_comment is None:
            module.fail_json(msg="snapshot_comment is required when updating a snapshot")

        snapshot = find_snapshot(module, storagebox_id, snapshot_name)
        if not snapshot:
            module.fail_json(msg="Snapshot with name {0} does not exist".format(snapshot_name))
        if snapshot_comment == snapshot['description']:
            module.exit_json(changed=False, snapshot=extract_legacy(snapshot))
        if not module.check_mode:
            url = "{0}/v1/storage_boxes/{1}/snapshots/{2}".format(API_BASE_URL, storagebox_id, snapshot['id'])
            headers = {"Content-type": "application/json"}
            result, dummy, dummy2 = api_fetch_url_json(
                module,
                url,
                method='PUT',
                data=module.jsonify({"description": snapshot_comment}),
                headers=headers,
            )
            snapshot = result["snapshot"]
        else:
            snapshot['description'] = snapshot_comment
        module.exit_json(changed=True, snapshot=extract_legacy(snapshot))

    # Delete snapshot
    else:
        snapshot = find_snapshot(module, storagebox_id, snapshot_name)
        if not snapshot:
            module.exit_json(changed=False)
        if not module.check_mode:
            action_url = "{0}/v1/storage_boxes/{1}/snapshots/{2}".format(API_BASE_URL, storagebox_id, snapshot['id'])
            try:
                api_apply_action(
                    module,
                    action_url,
                    None,
                    lambda action_id: "{0}/v1/storage_boxes/actions/{1}".format(API_BASE_URL, action_id),
                    method='DELETE',
                    check_done_delay=1,
                    check_done_timeout=120,
                )
            except ApplyActionError as exc:
                module.fail_json(msg='Error while deleting snapshot: {0}'.format(exc))
        module.exit_json(changed=True)


def find_snapshot(module, storagebox_id, snapshot_name):
    url = "{0}/v1/storage_boxes/{1}/snapshots?{2}".format(API_BASE_URL, storagebox_id, urlencode({'name': snapshot_name}))
    result, dummy, error = api_fetch_url_json(module, url, accept_errors=['not_found'])
    if error:
        module.fail_json(msg='Storagebox with ID {0} does not exist'.format(storagebox_id))
    snapshots = [snapshot for snapshot in result["snapshots"] if snapshot['name'] == snapshot_name]
    if len(snapshots) > 1:
        module.fail_json(msg='Found {0} snapshots with name {1!r}'.format(len(snapshots), snapshot_name))
    return snapshots[0] if snapshots else None


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
