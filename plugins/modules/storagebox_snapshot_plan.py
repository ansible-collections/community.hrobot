#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: storagebox_snapshot_plan
short_description: Modify a storage box's snapshot plans
version_added: 2.1.0
author:
  - Felix Fontein (@felixfontein)
description:
  - Enable, modify, and disable the snapshot plans of a storage box.
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
  storagebox_id:
    description:
      - The ID of the storage box to modify.
    type: int
    required: true
  plans:
    description:
      - The storage plan configurations.
      - Note that right now there must be exactly one element.
      - All date and time parameters are in UTC.
    type: list
    elements: dict
    required: true
    suboptions:
      status:
        description:
          - The status of the snapshot plan.
        type: str
        choices:
          - enabled
          - disabled
        required: true
      minute:
        description:
          - The minute of execution of the plan.
          - Required if O(plans[].status=enabled).
        type: int
      hour:
        description:
          - The hour of execution of the plan.
          - Required if O(plans[].status=enabled).
        type: int
      day_of_week:
        description:
          - The day of the week of execution of the plan. V(1) is Monday, V(7) is Sunday.
          - If set to V(null) or omitted, the plan is run every day of a week, unless there are other restrictions.
        type: int
      day_of_month:
        description:
          - The day of month of execution of the plan. V(1) is the 1st day of the month.
          - If set to V(null) or omitted, the plan is run every day of a month, unless there are other restrictions.
        type: int
      month:
        description:
          - The month of execution of the plan. V(1) is January, V(12) is December.
          - If set to V(null) or omitted, the plan is run every month.
        type: int
      max_snapshots:
        description:
          - The maximum number of automatic snapshots of this plan.
          - Required if O(plans[].status=enabled).
        type: int
"""

EXAMPLES = r"""
- name: Setup storagebox
  community.hrobot.storagebox_snapshot_plan:
    hetzner_user: foo
    hetzner_password: bar
    storagebox_id: 123
    plans:
      - status: enabled
        minute: 5
        hour: 12
        day_of_week: 2  # Tuesday
        max_snapshots: 2
"""

RETURN = r"""
plans:
  description:
    - The storage box's snapshot plan configurations.
    - All date and time parameters are in UTC.
  returned: success
  type: list
  elements: dict
  contains:
    status:
      description:
        - The status of the snapshot plan.
      type: str
      sample: enabled
      returned: success
      choices:
        - enabled
        - disabled
    minute:
      description:
        - The minute of execution of the plan.
      type: int
      sample: 5
      returned: success
    hour:
      description:
        - The hour of execution of the plan.
      type: int
      sample: 12
      returned: success
    day_of_week:
      description:
        - The day of the week of execution of the plan. V(1) is Monday, V(7) is Sunday.
        - If set to V(null), the plan is run every day of a week, unless there are other restrictions.
      type: int
      sample: 2
      returned: success
    day_of_month:
      description:
        - The day of month of execution of the plan. V(1) is the 1st day of the month.
        - If set to V(null), the plan is run every day of a month, unless there are other restrictions.
      type: int
      sample: null
      returned: success
    month:
      description:
        - The month of execution of the plan. V(1) is January, V(12) is December.
        - If set to V(null), the plan is run every month.
      type: int
      sample: null
      returned: success
    max_snapshots:
      description:
        - The maximum number of automatic snapshots of this plan.
      type: int
      sample: 2
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
    'status': ('status', 'status'),  # according to the API docs 'status' cannot be provided as input to POST, but that's not true
    'minute': ('minute', 'minute'),
    'hour': ('hour', 'hour'),
    'day_of_week': ('day_of_week', 'day_of_week'),
    'day_of_month': ('day_of_month', 'day_of_month'),
    'month': ('month', 'month'),
    'max_snapshots': ('max_snapshots', 'max_snapshots'),
}


def extract(result):
    sb = result['snapshotplan']
    return {key: sb.get(key) for key, dummy in PARAMETERS.values()}


def main():
    argument_spec = dict(
        storagebox_id=dict(type='int', required=True),
        plans=dict(
            type='list',
            elements='dict',
            required=True,
            options=dict(
                status=dict(type='str', required=True, choices=['enabled', 'disabled']),
                minute=dict(type='int'),
                hour=dict(type='int'),
                day_of_week=dict(type='int'),
                day_of_month=dict(type='int'),
                month=dict(type='int'),
                max_snapshots=dict(type='int'),
            ),
            required_if=[
                ('status', 'enabled', ('minute', 'hour', 'max_snapshots')),
            ],
        ),
    )
    argument_spec.update(ROBOT_DEFAULT_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    storagebox_id = module.params['storagebox_id']
    plans = module.params['plans']
    # TODO: If the API ever changes to support more than one plan, the following needs to
    #       be removed and the corresponding part in the documentation must be updated.
    if len(plans) != 1:
        module.fail_json(msg='`plans` must have exactly one element')

    url = "{0}/storagebox/{1}/snapshotplan".format(BASE_URL, storagebox_id)
    result, error = fetch_url_json(module, url, accept_errors=['STORAGEBOX_NOT_FOUND'])
    if error:
        module.fail_json(msg='Storagebox with ID {0} does not exist'.format(storagebox_id))

    # The documentation (https://robot.hetzner.com/doc/webservice/en.html#get-storagebox-storagebox-id-snapshotplan)
    # claims that the result is a list, but actually it is a dictionary. Convert it to a list of dicts if that's the case.
    if isinstance(result, dict):
        result = [result]

    before = [extract(plan) for plan in result]
    after = [
        {
            data_name: (
                plan[option_name]
                if plan['status'] == 'enabled' or option_name == 'status' else
                None
            )
            for option_name, (data_name, dummy) in PARAMETERS.items()
        }
        for plan in plans
    ]
    changes = []

    for index, plan in enumerate(after):
        existing_plan = before[index] if index < len(before) else {}
        plan_values = {}
        has_changes = False
        for data_name, change_name in PARAMETERS.values():
            before_value = existing_plan.get(data_name)
            after_value = plan[data_name]
            if before_value != after_value:
                has_changes = True
            if after_value is not None and change_name is not None:
                plan_values[change_name] = after_value
        if has_changes:
            if plan['status'] == 'disabled':
                # For some reason, minute and hour are required even for disabled plans,
                # even though the documentation says otherwise
                plan_values['minute'] = 0
                plan_values['hour'] = 0
            changes.append((index, plan_values))

    if changes and not module.check_mode:
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        # TODO: If the API ever changes to support more than one plan, the following need to change
        if len(changes) != 1:  # pragma: no cover
            raise AssertionError('Current implementation can handle only one plan')  # pragma: no cover
        actual_changes = changes[0][1]
        result, error = fetch_url_json(
            module,
            url,
            data=urlencode(actual_changes) if actual_changes else None,
            headers=headers,
            method='POST',
            accept_errors=['INVALID_INPUT'],
        )
        if error:
            invalid = result['error'].get('invalid') or []
            module.fail_json(msg='The values to update were invalid ({0})'.format(', '.join(invalid)))

        # The documentation (https://robot.hetzner.com/doc/webservice/en.html#post-storagebox-storagebox-id-snapshotplan)
        # claims that the result is a list, but actually it is a dictionary. Convert it to a list of dicts if that's the case.
        if isinstance(result, dict):
            result = [result]

        after = [extract(plan) for plan in result]

    module.exit_json(
        changed=bool(changes),
        plans=after,
        diff={
            'before': {'plans': before},
            'after': {'plans': after},
        },
    )


if __name__ == '__main__':  # pragma: no cover
    main()  # pragma: no cover
