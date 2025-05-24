#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: storagebox
short_description: Modify a storage box's basic configuration
version_added: 2.1.0
author:
  - Felix Fontein (@felixfontein)
description:
  - Modify a storage box's basic configuration.
extends_documentation_fragment:
  - community.hrobot.robot
  - community.hrobot.attributes
  - community.hrobot.attributes.actiongroup_robot
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  idempotent:
    support: full

options:
  id:
    description:
      - The ID of the storage box to modify.
    type: int
    required: true
  name:
    description:
      - The name of the storage box.
    type: str
  samba:
    description:
      - Whether the storage box is accessible through SAMBA.
    type: bool
  webdav:
    description:
      - Whether the storage box is accessible through WebDAV.
    type: bool
  ssh:
    description:
      - Whether the storage box is accessible through SSH.
    type: bool
  external_reachability:
    description:
      - Whether the storage box is externally reachable.
    type: bool
  zfs:
    description:
      - Whether the ZFS directory is visible.
    type: bool
"""

EXAMPLES = r"""
---
- name: Setup storagebox
  community.hrobot.storagebox:
    hetzner_user: foo
    hetzner_password: bar
    name: "My storage box"
    ssh: true
    samba: false
    webdav: false
    external_reachability: false
    zfs: false
"""

RETURN = r"""
name:
  description:
    - The storage box's name.
  type: str
  sample: Backup Server 1
  returned: success
webdav:
  description:
    - Whether WebDAV is active.
  type: bool
  sample: true
  returned: success
samba:
  description:
    - Whether SAMBA is active.
  type: bool
  sample: true
  returned: success
ssh:
  description:
    - Whether SSH is active.
  type: bool
  sample: true
  returned: success
external_reachability:
  description:
    - Whether the storage box is reachable externally.
  type: bool
  sample: true
  returned: success
zfs:
  description:
    - Shows whether the ZFS directory is visible.
  type: bool
  sample: false
  returned: success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode

from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    BASE_URL,
    ROBOT_DEFAULT_ARGUMENT_SPEC,
    fetch_url_json,
)


PARAMETERS = {
    'name': ('name', 'storagebox_name'),
    'webdav': ('webdav', 'webdav'),
    'samba': ('samba', 'samba'),
    'ssh': ('ssh', 'ssh'),
    'external_reachability': ('external_reachability', 'external_reachability'),
    'zfs': ('zfs', 'zfs'),
}


def extract(result):
    sb = result['storagebox']
    return {key: sb.get(key) for key, dummy in PARAMETERS.values()}


def main():
    argument_spec = dict(
        id=dict(type='int', required=True),
        name=dict(type='str'),
        samba=dict(type='bool'),
        webdav=dict(type='bool'),
        ssh=dict(type='bool'),
        external_reachability=dict(type='bool'),
        zfs=dict(type='bool'),
    )
    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    storagebox_id = module.params['id']
    url = "{0}/storagebox/{1}".format(BASE_URL, storagebox_id)
    result, error = fetch_url_json(module, url, accept_errors=['STORAGEBOX_NOT_FOUND'])
    if error:
        module.fail_json(msg='Storagebox with ID {0} does not exist'.format(storagebox_id))

    before = extract(result)
    after = dict(before)
    changes = {}

    for option_name, (data_name, change_name) in PARAMETERS.items():
        value = module.params[option_name]
        if value is not None:
            if before[data_name] != value:
                after[data_name] = value
                if isinstance(value, bool):
                    changes[change_name] = str(value).lower()
                else:
                    changes[change_name] = value

    if changes and not module.check_mode:
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        result, error = fetch_url_json(
            module,
            url,
            data=urlencode(changes),
            headers=headers,
            method='POST',
            accept_errors=['INVALID_INPUT'],
        )
        if error:
            invalid = result['error'].get('invalid') or []
            module.fail_json(msg='The values to update were invalid ({0})'.format(', '.join(invalid)))
        after = extract(result)

    result = dict(after)
    result['changed'] = bool(changes)
    result['diff'] = {
        'before': before,
        'after': after,
    }
    module.exit_json(**result)


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
