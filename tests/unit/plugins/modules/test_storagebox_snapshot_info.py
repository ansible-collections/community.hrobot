# Copyright (c) 2025 Matthias Hurdebise <matthias_hurdebise@hotmail.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.api import API_BASE_URL
from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot_info


LEGACY_STORAGEBOX_SNAPSHOTS = [
    {
        "snapshot": {
            "name": "2015-12-21T12-40-38",
            "timestamp": "2015-12-21T13:40:38+00:00",
            "size": 400,
            "filesystem_size": 12345,
            "automatic": False,
            "comment": "Test-Snapshot 1"
        }
    },
    {
        "snapshot": {
            "name": "2025-01-24T12-00-00",
            "timestamp": "2025-01-24T12:00:00+00:00",
            "size": 10000,
            "filesystem_size": 22345,
            "automatic": False,
            "comment": "Test-Snapshot 2"
        }
    }
]


STORAGEBOX_SNAPSHOTS = {
    "snapshots": [
        {
            "id": 1,
            "stats": {
                "size": 2097152,
                "size_filesystem": 1048576
            },
            "is_automatic": False,
            "name": "2025-02-12T11-35-19",
            "description": "my-description",
            "created": "2025-02-12T11:35:19.000Z",
            "storage_box": 42,
            "labels": {
                "environment": "prod",
                "example.com/my": "label",
                "just-a-key": None,
            }
        },
        {
            "id": 2,
            "stats": {
                "size": 2097152,
                "size_filesystem": 1048576
            },
            "is_automatic": True,
            "name": "snapshot-daily--2025-02-12T22-00-02",
            "description": "",
            "created": "2025-02-22:00:02.000Z",
            "storage_box": 42,
            "labels": {
                "environment": "prod",
                "example.com/my": "label",
                "just-a-key": None,
            }
        },
    ],
}


class TestHetznerStorageboxSnapshotPlanInfoLegacy(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_snapshot(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23}, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(LEGACY_STORAGEBOX_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['changed'] is False
        assert len(result['snapshots']) == 2
        assert result['snapshots'][0] == LEGACY_STORAGEBOX_SNAPSHOTS[0]['snapshot']

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storage Box with ID 23 does not exist',
                }
            })
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'


class TestHetznerStorageboxSnapshotPlanInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_snapshot(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 42,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_SNAPSHOTS)
            .expect_url('{0}/v1/storage_boxes/42/snapshots'.format(API_BASE_URL))
        ])
        assert result['changed'] is False
        assert len(result['snapshots']) == 2
        assert result['snapshots'] == [
            {
                'automatic': False,
                'comment': 'my-description',
                "created": "2025-02-12T11:35:19.000Z",
                "description": "my-description",
                'filesystem_size': 1,
                "id": 1,
                "is_automatic": False,
                "name": "2025-02-12T11-35-19",
                "labels": {
                    "environment": "prod",
                    "example.com/my": "label",
                    "just-a-key": None,
                },
                'size': 2,
                "stats": {
                    "size": 2097152,
                    "size_filesystem": 1048576
                },
                "storage_box": 42,
                "timestamp": "2025-02-12T11:35:19.000Z",
            },
            {
                'automatic': True,
                'comment': '',
                "created": "2025-02-22:00:02.000Z",
                "description": "",
                'filesystem_size': 1,
                "id": 2,
                "is_automatic": True,
                "name": "snapshot-daily--2025-02-12T22-00-02",
                "labels": {
                    "environment": "prod",
                    "example.com/my": "label",
                    "just-a-key": None,
                },
                'size': 2,
                "stats": {
                    "size": 2097152,
                    "size_filesystem": 1048576
                },
                "storage_box": 42,
                "timestamp": "2025-02-22:00:02.000Z",
            },
        ]

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_info, {
            'hetzner_token': '',
            'storagebox_id': 23
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                }
            })
            .expect_url('{0}/v1/storage_boxes/23/snapshots'.format(API_BASE_URL))
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'
