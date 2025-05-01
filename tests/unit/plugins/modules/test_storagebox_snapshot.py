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
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot

CREATED_SNAPSHOT = {
    'snapshot': {
        'name': '2025-03-28T15-20-51',
        'timestamp': '2025-03-28T16:20:51+01:00',
        'size': 0
    }
}

EXISTING_SNAPSHOTS = [
    {
        'snapshot': {
            'name': '2015-12-21T12-40-38',
            'timestamp': '2015-12-21T13:40:38+00:00',
            'size': 400,
            'filesystem_size': 12345,
            'automatic': False,
            'comment': 'Test-Snapshot 1'
        }
    },
    {
        'snapshot': {
            'name': '2025-03-28T15-20-51',
            'timestamp': '2025-03-28T15:19:30+00:00',
            'size': 10000,
            'filesystem_size': 22345,
            'automatic': False,
            'comment': 'Test-Snapshot 2'
        }
    }
]


class TestHetznerStorageboxSnapshotPlanInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_create_snapshot(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23}, [
            FetchUrlCall('POST', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(CREATED_SNAPSHOT)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['changed'] is True
        assert result['snapshot'] == CREATED_SNAPSHOT['snapshot']

    def test_create_snapshot_check_mode(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            '_ansible_check_mode': True}, [
        ])
        assert result['changed'] is True

    def test_create_snapshot_with_comment(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'snapshot_comment': 'On Creation Comment'}, [
            FetchUrlCall('POST', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(CREATED_SNAPSHOT)
            .expect_url(BASE_URL + '/storagebox/23/snapshot'),
            FetchUrlCall("POST", 200)
            .expect_url('{0}/storagebox/23/snapshot/{1}/comment'.format(BASE_URL, CREATED_SNAPSHOT['snapshot']['name']))
            .result_json({
                'snapshot': {
                    'name': '2025-03-28T15-20-51',
                    'timestamp': '2025-03-28T16:20:51+01:00',
                    'size': 0,
                    'comment': 'On Creation Comment'
                }})
        ])
        assert result['changed'] is True
        assert result['snapshot']['comment'] == 'On Creation Comment'

    def test_comment_snapshot(self, mocker):
        self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Changing Comment',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(EXISTING_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot'),
            FetchUrlCall('POST', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_url('{0}/storagebox/23/snapshot/{1}/comment'.format(BASE_URL, '2025-03-28T15-20-51'))
        ])

    def test_same_comment_snapshot(self, mocker):
        self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Test-Snapshot 2',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(EXISTING_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])

    def test_comment_snapshot_check_mode(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Changing Comment',
            '_ansible_check_mode': True
        }, [
            FetchUrlCall('GET', 200)
            .result_json(EXISTING_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot'),
        ])
        assert result['changed'] is True

    def test_comment_snapshot_nonexistent_storagebox(self, mocker):
        self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 54,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Changing Comment',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storagebox with ID 54 does not exist',
                }
            })
            .expect_url(BASE_URL + '/storagebox/54/snapshot')
        ])

    def test_delete_snapshot(self, mocker):
        self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent'
        }, [
            FetchUrlCall('GET', 200)
            .result_json(EXISTING_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot'),
            FetchUrlCall('DELETE', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_url('{0}/storagebox/23/snapshot/{1}'.format(BASE_URL, '2025-03-28T15-20-51'))
        ])

    def test_delete_snapshot_check_mode(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent',
            '_ansible_check_mode': True
        }, [
            FetchUrlCall('GET', 200)
            .result_json(EXISTING_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['changed'] is True

    def test_create_limit_exceeded(self, mocker):
        resutl = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('POST', 409)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_url('{0}/storagebox/23/snapshot'.format(BASE_URL))
        ])
        resutl['msg'] == 'Snapshot limit exceeded'

    def test_create_wihth_state_present(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'state': 'present'}, [
            FetchUrlCall('POST', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(CREATED_SNAPSHOT)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['changed'] is True
        assert result['snapshot'] == CREATED_SNAPSHOT['snapshot']

    def test_delete_nonexistent_snapshot(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'snapshot_name': 'does-not-exist',
            'state': 'absent'
        }, [
            FetchUrlCall("GET", 200)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
            .result_json(EXISTING_SNAPSHOTS)
        ])
        assert result['changed'] is False

    def test_delete_snapshot_nonexistent_storagebox(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 54,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent'
        }, [
            FetchUrlCall("GET", 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storagebox with ID 54 does not exist',
                }
            })
            .expect_url(BASE_URL + '/storagebox/54/snapshot')
        ])
        assert result['msg'] == 'Storagebox with ID 54 does not exist'

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 54
        }, [
            FetchUrlCall('POST', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storagebox with ID 54 does not exist',
                }
            })
            .expect_url(BASE_URL + '/storagebox/54/snapshot')
        ])
        assert result['msg'] == 'Storagebox with ID 54 does not exist'

    def test_snapshot_name_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'snapshot_name': '2038-01-19T03:14:17',
            'snapshot_comment': 'Test comment'
        }, [
            FetchUrlCall('GET', 200)
            .result_json(EXISTING_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['msg'] == 'Snapshot with name 2038-01-19T03:14:17 does not exist'

    def test_snapshot_name_with_state_present(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
            'snapshot_name': '2038-01-19T03:14:17',
            'state': 'present'
        }, [])
        assert result['msg'] == "snapshot_comment is required when updating a snapshot"
