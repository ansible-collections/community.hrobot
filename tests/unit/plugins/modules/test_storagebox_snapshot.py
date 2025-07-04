# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import MagicMock

from ansible_collections.community.hrobot.plugins.module_utils.api import API_BASE_URL
from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot

LEGACY_CREATED_SNAPSHOT = {
    'snapshot': {
        'name': '2025-03-28T15-20-51',
        'timestamp': '2025-03-28T16:20:51+01:00',
        'size': 0
    }
}

LEGACY_EXISTING_SNAPSHOTS = [
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


STORAGEBOX_SNAPSHOTS = {
    1: {
        "id": 1,
        "stats": {
            "size": 2097152,
            "size_filesystem": 1048576
        },
        "is_automatic": False,
        "name": "2015-12-21T12-40-38",
        "description": "Test-Snapshot 1",
        "created": "2025-02-12T11:35:19.000Z",
        "storage_box": 23,
        "labels": {}
    },
    2: {
        "id": 2,
        "stats": {
            "size": 2097152,
            "size_filesystem": 1048576
        },
        "is_automatic": False,
        "name": "2025-03-28T15-20-51",
        "description": "Test-Snapshot 2",
        "created": "2025-02-22:00:02.000Z",
        "storage_box": 23,
        "labels": {}
    },
}


class TestHetznerStorageboxSnapshotPlanInfoLegacy(BaseTestModule):
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
            .result_json(LEGACY_CREATED_SNAPSHOT)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['changed'] is True
        assert result['snapshot'] == LEGACY_CREATED_SNAPSHOT['snapshot']

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
            .result_json(LEGACY_CREATED_SNAPSHOT)
            .expect_url(BASE_URL + '/storagebox/23/snapshot'),
            FetchUrlCall("POST", 200)
            .expect_url('{0}/storagebox/23/snapshot/{1}/comment'.format(BASE_URL, LEGACY_CREATED_SNAPSHOT['snapshot']['name']))
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
            .result_json(LEGACY_EXISTING_SNAPSHOTS)
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
            .result_json(LEGACY_EXISTING_SNAPSHOTS)
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
            .result_json(LEGACY_EXISTING_SNAPSHOTS)
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
            .result_json(LEGACY_EXISTING_SNAPSHOTS)
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
            .result_json(LEGACY_EXISTING_SNAPSHOTS)
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

    def test_create_with_state_present(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
            'state': 'present'}, [
            FetchUrlCall('POST', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(LEGACY_CREATED_SNAPSHOT)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['changed'] is True
        assert result['snapshot'] == LEGACY_CREATED_SNAPSHOT['snapshot']

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
            .result_json(LEGACY_EXISTING_SNAPSHOTS)
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
            .result_json(LEGACY_EXISTING_SNAPSHOTS)
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


class TestHetznerStorageboxSnapshotPlanInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_create_snapshot(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('POST', 200)
            .expect_json_value_absent(['description'])
            .result_json({
                "action": {
                    "id": 13,
                    "command": "create_snapshot",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 2,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
                    "status": "success",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 2,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshot": STORAGEBOX_SNAPSHOTS[2],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots/2'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['snapshot'] == {
            'comment': 'Test-Snapshot 2',
            'filesystem_size': 1,
            'id': 2,
            'name': '2025-03-28T15-20-51',
            'size': 2,
            'timestamp': '2025-02-22:00:02.000Z',
        }

    def test_create_snapshot_check_mode(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            '_ansible_check_mode': True}, [
        ])
        assert result['changed'] is True

    def test_create_snapshot_with_comment(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_comment': 'On Creation Comment',
        }, [
            FetchUrlCall('POST', 200)
            .expect_json_value(['description'], 'On Creation Comment')
            .result_json({
                "action": {
                    "id": 13,
                    "command": "create_snapshot",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
                    "status": "success",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshot": STORAGEBOX_SNAPSHOTS[1],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots/1'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['snapshot'] == {
            'comment': 'Test-Snapshot 1',
            'filesystem_size': 1,
            'id': 1,
            'name': '2015-12-21T12-40-38',
            'size': 2,
            'timestamp': '2025-02-12T11:35:19.000Z',
        }

    def test_create_snapshot_failed(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('POST', 200)
            .expect_json_value_absent(['description'])
            .result_json({
                "action": {
                    "id": 13,
                    "command": "create_snapshot",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
                    "status": "error",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 42,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": {
                        "code": "action_failed",
                        "message": "Action failed",
                    },
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Error while creating snapshot: [action_failed] Action failed'

    def test_comment_snapshot(self, mocker):
        updated = dict(STORAGEBOX_SNAPSHOTS[2])
        updated['description'] = 'Changing Comment'
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Changing Comment',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[2],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 200)
            .result_json({
                "snapshot": updated,
            })
            .expect_json_value(['description'], 'Changing Comment')
            .expect_url('{0}/v1/storage_boxes/23/snapshots/2'.format(API_BASE_URL)),
        ])
        assert result['snapshot']['comment'] == 'Changing Comment'

    def test_same_comment_snapshot(self, mocker):
        self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Test-Snapshot 2',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[2],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
        ])

    def test_comment_snapshot_check_mode(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Changing Comment',
            '_ansible_check_mode': True
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[2],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True

    def test_comment_snapshot_nonexistent_storagebox(self, mocker):
        self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 54,
            'snapshot_name': '2025-03-28T15-20-51',
            'snapshot_comment': 'Changing Comment',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                "error": {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                },
            })
            .expect_url('{0}/v1/storage_boxes/54/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
        ])

    def test_delete_snapshot(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent'
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[2],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_snapshot",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 2,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots/2'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_snapshot",
                    "status": "success",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 2,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])

    def test_delete_snapshot_check_mode(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent',
            '_ansible_check_mode': True
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[2],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True

    def test_delete_snapshot_failed(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent'
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[2],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_snapshot",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 2,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots/2'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_snapshot",
                    "status": "error",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 2,
                            "type": "storage_box_snapshot",
                        },
                    ],
                    "error": {
                        "code": "action_failed",
                        "message": "Action failed",
                    },
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Error while deleting snapshot: [action_failed] Action failed'

    def test_create_limit_exceeded(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('POST', 400)
            .expect_json_value_absent(['description'])
            .result_json({
                "error": {
                    "code": "resource_limit_exceeded",
                    "message": "snapshot limit exceeded",
                    "details": {
                        "limits": [
                            {
                                "name": "snapshot_limit"
                            },
                        ],
                    },
                },
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots'.format(API_BASE_URL)),
        ])
        assert result['msg'] in (
            "Request failed: [resource_limit_exceeded] snapshot limit exceeded. Details: {'limits': [{'name': 'snapshot_limit'}]}",
            "Request failed: [resource_limit_exceeded] snapshot limit exceeded. Details: {u'limits': [{u'name': u'snapshot_limit'}]}",
        )

    def test_delete_nonexistent_snapshot(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': 'does not exist',
            'state': 'absent'
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[1],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=does+not+exist'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False

    def test_delete_snapshot_nonexistent_storagebox(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 54,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent'
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                "error": {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                },
            })
            .expect_url('{0}/v1/storage_boxes/54/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 54 does not exist'

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 54
        }, [
            FetchUrlCall('POST', 404)
            .result_json({
                "error": {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                },
            })
            .expect_url('{0}/v1/storage_boxes/54/snapshots'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 54 does not exist'

    def test_snapshot_name_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2038-01-19T03:14:17',
            'snapshot_comment': 'Test comment'
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2038-01-19T03%3A14%3A17'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Snapshot with name 2038-01-19T03:14:17 does not exist'

    def test_snapshot_name_with_state_present(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2038-01-19T03:14:17',
            'state': 'present'
        }, [])
        assert result['msg'] == "snapshot_comment is required when updating a snapshot"

    def test_multiple_names(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'snapshot_name': '2025-03-28T15-20-51',
            'state': 'absent'
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "snapshots": [
                    STORAGEBOX_SNAPSHOTS[2],
                    STORAGEBOX_SNAPSHOTS[2],
                ],
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots?name=2025-03-28T15-20-51'.format(API_BASE_URL)),
        ])
        assert result['msg'] == "Found 2 snapshots with name '2025-03-28T15-20-51'"
