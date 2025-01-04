# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot_plan


STORAGEBOX_PLAN_ENABLED = [
    {
        'snapshotplan': {
            'status': 'enabled',
            'minute': 5,
            'hour': 12,
            'day_of_week': 2,
            'day_of_month': None,
            'month': None,
            'max_snapshots': 2,
        },
    },
]

STORAGEBOX_PLAN_DISABLED = [
    {
        'snapshotplan': {
            'status': 'disabled',
            'minute': None,
            'hour': None,
            'day_of_week': None,
            'day_of_month': None,
            'month': None,
            'max_snapshots': None,
        },
    },
]


def update_plan(plan, **values):
    def update(p):
        p = dict(p)
        p.update(values)
        return p

    return [update(p) for p in plan]


class TestHetznerStorageboxSnapshotPlan(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot_plan.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_idempotent(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'plans': [
                STORAGEBOX_PLAN_ENABLED[0]['snapshotplan'],
            ],
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_PLAN_ENABLED)
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == STORAGEBOX_PLAN_ENABLED[0]['snapshotplan']

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1,
            'plans': [
                STORAGEBOX_PLAN_ENABLED[0]['snapshotplan'],
            ],
        }, [
            FetchUrlCall('GET', 404)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storagebox not found',
                },
            })
            .expect_url('{0}/storagebox/1/snapshotplan'.format(BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 1 does not exist'

    def test_wrong_number_of_plans(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'plans': [],
        }, [
        ])
        assert result['msg'] == '`plans` must have exactly one element'

    def test_invalid_input(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'plans': [
                {
                    'status': 'enabled',
                    'hour': 25,
                    'minute': 0,
                    'max_snapshots': -1,
                },
            ],
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            # The actual API does not return a list, but its only entry directly
            .result_json(STORAGEBOX_PLAN_ENABLED[0])
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
            FetchUrlCall('POST', 400)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json({
                'error': {
                    'status': 400,
                    'code': 'INVALID_INPUT',
                    'message': 'Invalid input',
                    'invalid': ['hour', 'max_snapshots'],
                    'missing': None,
                },
            })
            .expect_form_value('status', 'enabled')
            .expect_form_value('hour', '25')
            .expect_form_value('minute', '0')
            .expect_form_value_absent('day_of_week')
            .expect_form_value_absent('day_of_month')
            .expect_form_value_absent('month')
            .expect_form_value('max_snapshots', '-1')
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The values to update were invalid (hour, max_snapshots)'

    def test_disable(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'plans': [
                {
                    'status': 'disabled',
                },
            ],
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_PLAN_ENABLED)
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
            FetchUrlCall('POST', 400)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_PLAN_DISABLED)
            .expect_form_value('status', 'disabled')
            .expect_form_value('hour', '0')  # should be absent, but API does not permit that
            .expect_form_value('minute', '0')  # should be absent, but API does not permit that
            .expect_form_value_absent('day_of_week')
            .expect_form_value_absent('day_of_month')
            .expect_form_value_absent('month')
            .expect_form_value_absent('max_snapshots')
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert len(result['plans']) == 1
        assert result['plans'][0] == STORAGEBOX_PLAN_DISABLED[0]['snapshotplan']

    def test_enable(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'plans': [
                {
                    'status': 'enabled',
                    'minute': 5,
                    'hour': 12,
                    'day_of_week': 2,
                    'max_snapshots': 2,
                },
            ],
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_PLAN_DISABLED)
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
            FetchUrlCall('POST', 400)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_PLAN_ENABLED)
            .expect_form_value('status', 'enabled')
            .expect_form_value('hour', '12')
            .expect_form_value('minute', '5')
            .expect_form_value('day_of_week', '2')
            .expect_form_value_absent('day_of_month')
            .expect_form_value_absent('month')
            .expect_form_value('max_snapshots', '2')
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert len(result['plans']) == 1
        assert result['plans'][0] == STORAGEBOX_PLAN_ENABLED[0]['snapshotplan']

    def test_change(self, mocker):
        updated_plan = update_plan(STORAGEBOX_PLAN_ENABLED, day_of_week=None, day_of_month=1)
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'plans': [
                {
                    'status': 'enabled',
                    'minute': 5,
                    'hour': 12,
                    'day_of_month': 1,
                    'month': None,
                    'max_snapshots': 2,
                },
            ],
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_PLAN_ENABLED)
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
            FetchUrlCall('POST', 400)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            # The actual API does not return a list, but its only entry directly
            .result_json(updated_plan[0])
            .expect_form_value('status', 'enabled')
            .expect_form_value('hour', '12')
            .expect_form_value('minute', '5')
            .expect_form_value_absent('day_of_week')
            .expect_form_value('day_of_month', '1')
            .expect_form_value_absent('month')
            .expect_form_value('max_snapshots', '2')
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert len(result['plans']) == 1
        assert result['plans'][0] == updated_plan[0]['snapshotplan']
