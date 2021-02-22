#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c), name <email>, year
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: rdns
short_description: Manage Hetzner's dedicated server reverse DNS entries
author:
  - WIP
description:
  - Manage Hetzner's dedicated server reverse DNS entries.
seealso:
  - name: Reverse DNS documentation
    description: Hetzner's documentation on reverse DNS.
    link: https://docs.hetzner.com/dns-console/dns/general/reverse-dns
extends_documentation_fragment:
- community.hrobot.robot

options:
  ip_address:
    description: The IP address that should point to I(rdns).
    type: str
    required: yes
  rdns:
    description:
      - The DNS address the I(ip_address) should resolve to.
      - Omit the param to reset the reverse DNS entry to the default value.
    type: str
  state:
    description:
      - State of the reverse DNS entry.
     type: str
     choices: [ absent, present ]
     default: present
  timeout:
    description:
      - Timeout to use when creating, updating or deleting the reverse DNS.
    type: int
    default: 180
'''

EXAMPLES = r'''
- name: Create a reverse DNS entry for a server
  community.hrobot.rdns:
    hetzner_user: foo
    hetzner_password: bar
    ip_address: 1.2.3.4
    rdns: example.com

- name: Ensure the reverse DNS entry is absent (remove if needed)
  community.hrobot.rdns:
    hetzner_user: foo
    hetzner_password: bar
    ip_address: 1.2.3.4
    rdns: example.com
    state: absent
'''

RETURN = r'''
ip_address:
  description:
    - The IP address that point to the DNS ptr
  returned: always
  type: str
  sample: 1.2.3.4
rdns:
  description:
    - The DNS that resolves to the IP
  returned: always
  type: str
  sample: example.com
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.hrobot.plugins.module_utils.robot import (
    ROBOT_DEFAULT_ARGUMENT_SPEC,
)
from ansible_collections.community.hrobot.plugins.module_utils.rdns import (
    get_rdns,
    set_rdns,
)


def main():
    argument_spec = dict(
        ip_address=dict(type='str', required=True),
        rdns=dict(type='str'),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        timeout=dict(type='int', default=180),
    )
    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    ip_address = module.params['ip_address']
    changed = False
    rdns = get_rdns(module, ip_address)
    before = rdns

    if module.params['state'] == 'absent':
        new_rdns = None
    elif module.params['state'] == 'present':
        new_rdns = module.params['rdns']

    if rdns != new_rdns:
        if module.check_mode:
            rdns = new_rdns
            changed = True
        else:
            changed = set_rdns(module, ip_address, new_rdns, timeout=module.params['timeout'])

    after = get_rdns(module, ip_address)
    if before == after:
        changed = False
    module.exit_json(
        changed=changed,
        rdns=dict(
            ip_address=ip_address,
            rdns=rdns,
        ),
    )


if __name__ == '__main__':
    main()
