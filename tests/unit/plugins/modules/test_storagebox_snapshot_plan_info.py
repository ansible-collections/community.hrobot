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
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot_plan_info


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


class TestHetznerStorageboxSnapshotPlanInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot_plan_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_regular_enabled(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
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

    def test_regular_disabled(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_PLAN_DISABLED)
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == STORAGEBOX_PLAN_DISABLED[0]['snapshotplan']

    def test_actual_enabled(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            # The actual API does not return a list, but its only entry directly
            .result_json(STORAGEBOX_PLAN_ENABLED[0])
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == STORAGEBOX_PLAN_ENABLED[0]['snapshotplan']

    def test_actual_disabled(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            # The actual API does not return a list, but its only entry directly
            .result_json(STORAGEBOX_PLAN_DISABLED[0])
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == STORAGEBOX_PLAN_DISABLED[0]['snapshotplan']

    def test_server_number_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'
