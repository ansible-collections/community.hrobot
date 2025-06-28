# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import call, MagicMock

from ansible_collections.community.hrobot.plugins.module_utils.api import API_BASE_URL
from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import storagebox_info


STORAGEBOX_MINIMUM_DATA = [
    {
        'storagebox': {
            'id': 123456,
            'login': 'u12345',
            'name': 'Backup Server 1',
            'product': 'BX60',
            'cancelled': False,
            'locked': False,
            'location': 'FSN1',
            'linked_server': 1234567,
            'paid_until': '2015-10-23',
        },
    },
    {
        'storagebox': {
            'id': 23,
            'login': 'u23',
            'name': 'Backup Server 2',
            'product': 'BX11',
            'cancelled': True,
            'locked': False,
            'location': 'HEL1',
            'linked_server': None,
            'paid_until': '2025-01-31',
        },
    },
]


STORAGEBOX_DETAIL_DATA = {
    23: {
        'storagebox': {
            'id': 23,
            'login': 'u23',
            'name': 'Backup Server 2',
            'product': 'BX11',
            'cancelled': True,
            'locked': False,
            'location': 'HEL1',
            'linked_server': None,
            'paid_until': '2025-01-31',
            'disk_quota': 1234,
            'disk_usage': 123,
            'disk_usage_data': 50,
            'disk_usage_snapshots': 73,
            'webdav': False,
            'samba': False,
            'ssh': True,
            'external_reachability': True,
            'zfs': False,
            'server': 'u23.your-storagebox.de',
            'host_system': 'HEL1-FOOBAR'
        },
    },
    123456: {
        'storagebox': {
            'id': 123456,
            'login': 'u12345',
            'name': 'Backup Server 1',
            'product': 'BX60',
            'cancelled': False,
            'locked': False,
            'location': 'FSN1',
            'linked_server': 1234567,
            'paid_until': '2015-10-23',
            'disk_quota': 10240000,
            'disk_usage': 900,
            'disk_usage_data': 500,
            'disk_usage_snapshots': 400,
            'webdav': True,
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'zfs': False,
            'server': 'u12345.your-storagebox.de',
            'host_system': 'FSN1-BX355'
        },
    },
}

STORAGEBOX_API_DATA = {
    23: {
        'id': 23,
        'username': 'u23',
        'status': 'active',
        'name': 'string',
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
            'reachable_externally': False,
            'samba_enabled': False,
            'ssh_enabled': True,
            'webdav_enabled': False,
            'zfs_enabled': False,
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
            'minute': None,
            'hour': None,
            'day_of_week': None,
            'day_of_month': None,
        },
        'created': '2016-01-30T23:55:00+00:00',
    },
    123456: {
        'id': 123456,
        'username': 'u123456',
        'status': 'active',
        'name': 'string',
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
            'id': 23,
            'name': 'hel1',
            'description': 'Helsinki somewhere',
            'country': 'FI',
            'city': 'Helsinki',
            'latitude': 60.17,
            'longitude': 24.93,
            'network_zone': 'eu-central',
        },
        'access_settings': {
            'reachable_externally': False,
            'samba_enabled': True,
            'ssh_enabled': True,
            'webdav_enabled': True,
            'zfs_enabled': True,
        },
        'server': 'u123456.your-storagebox.de',
        'system': 'FSN1-BX355',
        'stats': {
            'size': 0,
            'size_data': 0,
            'size_snapshots': 0,
        },
        'labels': {
        },
        'protection': {
            'delete': False,
        },
        'snapshot_plan': {
            'max_snapshots': 0,
            'minute': None,
            'hour': None,
            'day_of_week': None,
            'day_of_month': None,
        },
        'created': '2025-06-28T23:55:00+00:00',
    },
}


class TestHetznerStorageboxInfoLegacy(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_storagebox_id(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 1
        assert result['storageboxes'][0] == STORAGEBOX_DETAIL_DATA[23]['storagebox']

    def test_server_number_unknown(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_url('{0}/storagebox/1'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0

    def test_all(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_MINIMUM_DATA)
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 2
        assert result['storageboxes'][0] == STORAGEBOX_MINIMUM_DATA[0]['storagebox']
        assert result['storageboxes'][1] == STORAGEBOX_MINIMUM_DATA[1]['storagebox']

    def test_linked_server_number(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'linked_server_number': 1234567,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_MINIMUM_DATA[0])
            .expect_form_value('linked_server', '1234567')
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 1
        assert result['storageboxes'][0] == STORAGEBOX_MINIMUM_DATA[0]['storagebox']

    def test_linked_server_number_unknown(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'linked_server_number': 1,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_form_value('linked_server', '1')
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0

    def test_all_full_info(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'full_info': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_MINIMUM_DATA)
            .expect_url('{0}/storagebox'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_DETAIL_DATA[123456])
            .expect_url('{0}/storagebox/123456'.format(BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 2
        assert result['storageboxes'][0] == STORAGEBOX_DETAIL_DATA[123456]['storagebox']
        assert result['storageboxes'][1] == STORAGEBOX_DETAIL_DATA[23]['storagebox']

    def test_all_none(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json([])
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0

    def test_all_none_error(self, mocker):
        # According to the API docs, when no storagebox is found this API can return 404.
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_user': '',
            'hetzner_password': '',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'server not found',
                },
            })
            .expect_url('{0}/storagebox'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0


class TestHetznerStorageboxInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_auth_error(self, mocker):
        result = self.run_module_failed(mocker, storagebox_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 401)
            .expect_header("Authorization", "Bearer asdf")
            .result_json({
                "error": {
                    "code": "unauthorized",
                    "details": None,
                    "message": "unable to authenticate",
                },
            })
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Request failed: [unauthorized] unable to authenticate'

    def test_auth_error_w_details(self, mocker):
        result = self.run_module_failed(mocker, storagebox_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 401)
            .expect_header("Authorization", "Bearer asdf")
            .result_json({
                "error": {
                    "code": "unauthorized",
                    "details": {
                        "username": "invalid",
                    },
                    "message": "unable to authenticate",
                },
            })
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] in (
            "Request failed: [unauthorized] unable to authenticate. Details: {'username': 'invalid'}",
            "Request failed: [unauthorized] unable to authenticate. Details: {u'username': u'invalid'}",
        )

    def test_empty_result(self, mocker):
        result = self.run_module_failed(mocker, storagebox_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_header("Authorization", "Bearer asdf")
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Cannot retrieve content from GET https://api.hetzner.com/v1/storage_boxes/23, HTTP status code 200 (None)'

    def test_empty_result_rate_limited(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
            'rate_limit_retry_timeout': 1,
        }, [
            FetchUrlCall('GET', 429)
            .expect_header("Authorization", "Bearer asdf")
            .result_error_json('Not found', {
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .return_header('RateLimit-Limit', '23')
            .return_header('RateLimit-Remaining', '0')
            .return_header('RateLimit-Reset', '1234567890')
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .expect_header("Authorization", "Bearer asdf")
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Cannot retrieve content from GET https://api.hetzner.com/v1/storage_boxes/23, HTTP status code 200 (None)'
        # TODO: only works with Python 3+
        # sleep_mock.assert_called_once()

    def test_empty_result_rate_limited_error(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
            'rate_limit_retry_timeout': 0,
        }, [
            FetchUrlCall('GET', 429)
            .result_error_json('Not found', {
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .return_header('RateLimit-Limit', '23')
            .return_header('RateLimit-Remaining', '0')
            .return_header('RateLimit-Reset', '1234567890')
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Request failed: [rate_limit_exceeded] Rate limit exceeded'
        sleep_mock.assert_has_calls([])

    def test_bad_json(self, mocker):
        result = self.run_module_failed(mocker, storagebox_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_header("Authorization", "Bearer asdf")
            .result_str("{")
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Cannot decode content retrieved from https://api.hetzner.com/v1/storage_boxes/23'

    def test_storagebox_id(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_header("Authorization", "Bearer asdf")
            .result_json({
                "storage_box": STORAGEBOX_API_DATA[23],
            })
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 1
        assert result['storageboxes'][0] == storagebox_info.add_hrobot_compat_shim(STORAGEBOX_API_DATA[23])

    def test_server_number_unknown(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_token': '',
            'storagebox_id': 1,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                },
            })
            .expect_url('{0}/v1/storage_boxes/1'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0

    def test_all(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_token': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "storage_boxes": [
                    STORAGEBOX_API_DATA[23],
                    STORAGEBOX_API_DATA[123456],
                ],
                "meta": {
                    "pagination": {
                        "page": 1,
                        "per_page": 100,
                        "previous_page": None,
                        "next_page": None,
                        "last_page": 1,
                        "total_entries": 2,
                    },
                },
            })
            .expect_url('{0}/v1/storage_boxes?page=1&per_page=100'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 2
        assert result['storageboxes'][0] == storagebox_info.add_hrobot_compat_shim(STORAGEBOX_API_DATA[23])
        assert result['storageboxes'][1] == storagebox_info.add_hrobot_compat_shim(STORAGEBOX_API_DATA[123456])

    def test_all_paginated(self, mocker):
        # This is kind of faked, since we ask for 100 entries per page, but get one entry per page...
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_token': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "storage_boxes": [
                    STORAGEBOX_API_DATA[23],
                ],
                "meta": {
                    "pagination": {
                        "page": 1,
                        "per_page": 100,
                        "previous_page": None,
                        "next_page": 2,
                        "last_page": 2,
                        "total_entries": 2,
                    },
                },
            })
            .expect_url('{0}/v1/storage_boxes?page=1&per_page=100'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "storage_boxes": [
                    STORAGEBOX_API_DATA[123456],
                ],
                "meta": {
                    "pagination": {
                        "page": 2,
                        "per_page": 100,
                        "previous_page": 1,
                        "next_page": None,
                        "last_page": 2,
                        "total_entries": 2,
                    },
                },
            })
            .expect_url('{0}/v1/storage_boxes?page=2&per_page=100'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 2
        assert result['storageboxes'][0] == storagebox_info.add_hrobot_compat_shim(STORAGEBOX_API_DATA[23])
        assert result['storageboxes'][1] == storagebox_info.add_hrobot_compat_shim(STORAGEBOX_API_DATA[123456])

    def test_all_paginated_strange(self, mocker):
        # This is really faked and simply tests more edge cases that should never happen with the real API
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_token': '',
            'rate_limit_retry_timeout': -1,
        }, [
            FetchUrlCall('GET', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .return_header('RateLimit-Limit', '23')
            .return_header('RateLimit-Remaining', '0')
            .return_header('RateLimit-Reset', '1234567890')
            .expect_url('{0}/v1/storage_boxes?page=1&per_page=100'.format(API_BASE_URL)),
            FetchUrlCall('GET', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .return_header('RateLimit-Limit', '23')
            .return_header('RateLimit-Remaining', '0')
            .return_header('RateLimit-Reset', '1234567891')
            .expect_url('{0}/v1/storage_boxes?page=1&per_page=100'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "storage_boxes": [
                    STORAGEBOX_API_DATA[23],
                    STORAGEBOX_API_DATA[123456],
                ],
            })
            .expect_url('{0}/v1/storage_boxes?page=1&per_page=100'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "storage_boxes": None,
                "meta": {
                    "pagination": {},
                },
            })
            .expect_url('{0}/v1/storage_boxes?page=2&per_page=100'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({})
            .expect_url('{0}/v1/storage_boxes?page=3&per_page=100'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 2
        assert result['storageboxes'][0] == storagebox_info.add_hrobot_compat_shim(STORAGEBOX_API_DATA[23])
        assert result['storageboxes'][1] == storagebox_info.add_hrobot_compat_shim(STORAGEBOX_API_DATA[123456])
        sleep_mock.assert_has_calls([
            call(5),
            call(5),
        ])

    def test_all_none(self, mocker):
        result = self.run_module_success(mocker, storagebox_info, {
            'hetzner_token': '',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "storage_boxes": [],
                "meta": {
                    "pagination": {
                        "page": 1,
                        "per_page": 100,
                        "previous_page": None,
                        "next_page": None,
                        "last_page": 1,
                        "total_entries": 0,
                    },
                },
            })
            .expect_url('{0}/v1/storage_boxes?page=1&per_page=100'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        assert len(result['storageboxes']) == 0
