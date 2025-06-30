# Copyright (c) 2025 Victor LEFEBVRE <dev@vic1707.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.api import API_BASE_URL
from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import (
    storagebox_subaccount_info,
)

LEGACY_STORAGEBOX_SUBACCOUNTS = [
    {
        "subaccount": {
            "username": "u2342-sub1",
            "accountid": "u2342",
            "server": "u12345-sub1.your-storagebox.de",
            "homedirectory": "test",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": False,
            "readonly": False,
            "createtime": "2017-05-24 00:00:00",
            "comment": "Test account",
        }
    },
    {
        "subaccount": {
            "username": "u2342-sub2",
            "accountid": "u2342",
            "server": "u12345-sub2.your-storagebox.de",
            "homedirectory": "test2",
            "samba": False,
            "ssh": True,
            "external_reachability": True,
            "webdav": True,
            "readonly": False,
            "createtime": "2025-01-24 00:00:00",
            "comment": "Test account 2",
        }
    },
]

STORAGEBOX_SUBACCOUNTS = {
    "subaccounts": [
        {
            "id": 42,
            "username": "u1337-sub1",
            "server": "u1337-sub1.your-storagebox.de",
            "home_directory": "my_backups/host01.my.company",
            "access_settings": {
                "samba_enabled": False,
                "ssh_enabled": True,
                "webdav_enabled": False,
                "reachable_externally": True,
                "readonly": False,
            },
            "description": "host01 backup",
            "created": "2025-02-22:00:02.000Z",
            "labels": {
                "environment": "prod",
                "example.com/my": "label",
                "just-a-key": None,
            },
            "storage_box": 42,
        },
    ],
}


class TestHetznerStorageboxSubbacountInfoLegacy(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_subaccount_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_subaccounts(self, mocker):
        result = self.run_module_success(mocker, storagebox_subaccount_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23}, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
            .expect_url(BASE_URL + '/storagebox/23/subaccount')
        ])
        assert result['changed'] is False
        assert len(result['subaccounts']) == 2
        assert result['subaccounts'][0] == LEGACY_STORAGEBOX_SUBACCOUNTS[0]['subaccount']

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount_info, {
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
            .expect_url(BASE_URL + '/storagebox/23/subaccount')
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'


class TestHetznerStorageboxSubbacountInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_subaccount_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_subaccounts(self, mocker):
        result = self.run_module_success(mocker, storagebox_subaccount_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_SUBACCOUNTS)
            .expect_url('{0}/v1/storage_boxes/23/subaccounts'.format(API_BASE_URL))
        ])
        assert result['changed'] is False
        assert len(result['subaccounts']) == 1
        assert result['subaccounts'] == [
            {
                "id": 42,
                "username": "u1337-sub1",
                "server": "u1337-sub1.your-storagebox.de",
                "home_directory": "my_backups/host01.my.company",
                "access_settings": {
                    "samba_enabled": False,
                    "ssh_enabled": True,
                    "webdav_enabled": False,
                    "reachable_externally": True,
                    "readonly": False,
                },
                "description": "host01 backup",
                "created": "2025-02-22:00:02.000Z",
                "labels": {
                    "environment": "prod",
                    "example.com/my": "label",
                    "just-a-key": None,
                },
                "storage_box": 42,
                'comment': 'host01 backup',
                'createtime': '2025-02-22:00:02.000Z',
                'external_reachability': True,
                'homedirectory': 'my_backups/host01.my.company',
                'readonly': False,
                'samba': False,
                'ssh': True,
                'webdav': False,
            },
        ]

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount_info, {
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
            .expect_url('{0}/v1/storage_boxes/23/subaccounts'.format(API_BASE_URL))
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'
