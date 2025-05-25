# Copyright (c) 2025 Matthias Hurdebise <matthias_hurdebise@hotmail.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot_info


STORAGEBOX_SNAPSHOTS = [
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


class TestHetznerStorageboxSnapshotPlanInfo(BaseTestModule):
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
            .result_json(STORAGEBOX_SNAPSHOTS)
            .expect_url(BASE_URL + '/storagebox/23/snapshot')
        ])
        assert result['changed'] is False
        assert len(result['snapshots']) == 2
        assert result['snapshots'][0] == STORAGEBOX_SNAPSHOTS[0]['snapshot']

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
