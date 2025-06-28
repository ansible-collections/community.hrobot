# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
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
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot_plan_info


LEGACY_STORAGEBOX_PLAN_ENABLED = [
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

LEGACY_STORAGEBOX_PLAN_DISABLED = [
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

STORAGEBOX_PLAN_ENABLED = {
    "storage_box": {
        'id': 23,
        'username': 'u23',
        'status': 'active',
        'name': 'Backup Server 2',
        'storage_box_type': {
            'name': 'bx11',
            'description': 'BX11',
            'snapshot_limit': 10,
            'automatic_snapshot_limit': 10,
            'subaccounts_limit': 200,
            'size': 1073741824,
            'prices': [
                {
                    'location': 'fsn1',
                    'price_hourly': {
                        'net': '1.0000',
                        'gross': '1.1900',
                    },
                    'price_monthly': {
                        'net': '1.0000',
                        'gross': '1.1900',
                    },
                    'setup_fee': {
                        'net': '1.0000',
                        'gross': '1.1900',
                    },
                },
            ],
            'deprecation': {
                'unavailable_after': '2023-09-01T00:00:00+00:00',
                'announced': '2023-06-01T00:00:00+00:00',
            },
        },
        'location': {
            'id': 42,
            'name': 'fsn1',
            'description': 'Falkenstein DC Park 1',
            'country': 'DE',
            'city': 'Falkenstein',
            'latitude': 50.47612,
            'longitude': 12.370071,
            'network_zone': 'eu-central',
        },
        'access_settings': {
            'reachable_externally': True,
            'samba_enabled': False,
            'ssh_enabled': True,
            'webdav_enabled': False,
            'zfs_enabled': True,
        },
        'server': 'u23.your-storagebox.de',
        'system': 'FSN1-BX355',
        'stats': {
            'size': 0,
            'size_data': 0,
            'size_snapshots': 0,
        },
        'labels': {
            'environment': 'prod',
            'example.com/my': 'label',
            'just-a-key': '',
        },
        'protection': {
            'delete': False,
        },
        'snapshot_plan': {
            'max_snapshots': 0,
            'minute': 10,
            'hour': 1,
            'day_of_week': None,
            'day_of_month': 5,
        },
        'created': '2016-01-30T23:55:00+00:00',
    },
}

STORAGEBOX_PLAN_DISABLED = {
    "storage_box": {
        'id': 23,
        'username': 'u23',
        'status': 'active',
        'name': 'Backup Server 2',
        'storage_box_type': {
            'name': 'bx11',
            'description': 'BX11',
            'snapshot_limit': 10,
            'automatic_snapshot_limit': 10,
            'subaccounts_limit': 200,
            'size': 1073741824,
            'prices': [
                {
                    'location': 'fsn1',
                    'price_hourly': {
                        'net': '1.0000',
                        'gross': '1.1900',
                    },
                    'price_monthly': {
                        'net': '1.0000',
                        'gross': '1.1900',
                    },
                    'setup_fee': {
                        'net': '1.0000',
                        'gross': '1.1900',
                    },
                },
            ],
            'deprecation': {
                'unavailable_after': '2023-09-01T00:00:00+00:00',
                'announced': '2023-06-01T00:00:00+00:00',
            },
        },
        'location': {
            'id': 42,
            'name': 'fsn1',
            'description': 'Falkenstein DC Park 1',
            'country': 'DE',
            'city': 'Falkenstein',
            'latitude': 50.47612,
            'longitude': 12.370071,
            'network_zone': 'eu-central',
        },
        'access_settings': {
            'reachable_externally': True,
            'samba_enabled': False,
            'ssh_enabled': True,
            'webdav_enabled': False,
            'zfs_enabled': True,
        },
        'server': 'u23.your-storagebox.de',
        'system': 'FSN1-BX355',
        'stats': {
            'size': 0,
            'size_data': 0,
            'size_snapshots': 0,
        },
        'labels': {
            'environment': 'prod',
            'example.com/my': 'label',
            'just-a-key': '',
        },
        'protection': {
            'delete': False,
        },
        'snapshot_plan': None,
        'created': '2016-01-30T23:55:00+00:00',
    },
}


class TestHetznerStorageboxSnapshotPlanInfoLegacy(BaseTestModule):
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
            .result_json(LEGACY_STORAGEBOX_PLAN_ENABLED)
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == LEGACY_STORAGEBOX_PLAN_ENABLED[0]['snapshotplan']

    def test_regular_disabled(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(LEGACY_STORAGEBOX_PLAN_DISABLED)
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == LEGACY_STORAGEBOX_PLAN_DISABLED[0]['snapshotplan']

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
            .result_json(LEGACY_STORAGEBOX_PLAN_ENABLED[0])
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == LEGACY_STORAGEBOX_PLAN_ENABLED[0]['snapshotplan']

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
            .result_json(LEGACY_STORAGEBOX_PLAN_DISABLED[0])
            .expect_url('{0}/storagebox/23/snapshotplan'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == LEGACY_STORAGEBOX_PLAN_DISABLED[0]['snapshotplan']

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


class TestHetznerStorageboxSnapshotPlanInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot_plan_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_enabled(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_header("Authorization", "Bearer asdf")
            .result_json(STORAGEBOX_PLAN_ENABLED)
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == {
            'status': 'enabled',
            'max_snapshots': 0,
            'minute': 10,
            'hour': 1,
            'day_of_week': None,
            'day_of_month': 5,
            'month': None,
        }

    def test_disabled(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_header("Authorization", "Bearer asdf")
            .result_json(STORAGEBOX_PLAN_DISABLED)
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['plans']) == 1
        assert result['plans'][0] == {
            'status': 'disabled',
            'max_snapshots': None,
            'minute': None,
            'hour': None,
            'day_of_week': None,
            'day_of_month': None,
            'month': None,
        }

    def test_server_number_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan_info, {
            'hetzner_token': '',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                },
            })
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'
