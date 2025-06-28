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
from ansible_collections.community.hrobot.plugins.modules import storagebox


STORAGEBOX_LEGACY_KEYS = ('name', 'webdav', 'samba', 'ssh', 'external_reachability', 'zfs')

STORAGEBOX_LEGACY_DETAIL_DATA = {
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

STORAGEBOX_KEYS = {
    'name': ['name'],
    'webdav': ['access_settings', 'webdav_enabled'],
    'samba': ['access_settings', 'samba_enabled'],
    'ssh': ['access_settings', 'ssh_enabled'],
    'external_reachability': ['access_settings', 'reachable_externally'],
    'zfs': ['access_settings', 'zfs_enabled'],
}

STORAGEBOX_DETAIL_DATA = {
    23: {
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
        'name': 'Backup Server 1',
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
            'reachable_externally': True,
            'samba_enabled': True,
            'ssh_enabled': True,
            'webdav_enabled': True,
            'zfs_enabled': False,
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


def legacy_update_info(id, **updates):
    result = {
        'storagebox': dict(STORAGEBOX_LEGACY_DETAIL_DATA[id]['storagebox']),
    }
    result['storagebox'].update(updates)
    return result


def update_info(id, **updates):
    result = {
        'storage_box': dict(STORAGEBOX_DETAIL_DATA[id]),
    }
    for k, v in updates.items():
        keys = STORAGEBOX_KEYS[k]
        dest = result['storage_box']
        for key in keys[:-1]:
            dest, old_dest = dict(dest[key]), dest
            old_dest[key] = dest
        dest[keys[-1]] = v
    return result


def get_key(data, key):
    for k in key:
        data = data[k]
    return data


class TestHetznerStorageboxLegacy(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_idempotent(self, mocker):
        updated = legacy_update_info(23)
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup Server 2',
            'webdav': False,
            'samba': False,
            'ssh': True,
            'external_reachability': True,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_LEGACY_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        for key in STORAGEBOX_LEGACY_KEYS:
            assert result[key] == updated['storagebox'][key], "Unexpected difference for {0!r}".format(key)

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_user': '',
            'hetzner_password': '',
            'id': 1,
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
            .expect_url('{0}/storagebox/1'.format(BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 1 does not exist'

    def test_invalid_input(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_user': '',
            'hetzner_password': '',
            'id': 23,
            'name': 'Backup',
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_LEGACY_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 400)
            .expect_basic_auth('', '')
            .expect_force_basic_auth(True)
            .result_json({
                'error': {
                    'status': 400,
                    'code': 'INVALID_INPUT',
                    'message': 'Invalid input',
                    'invalid': ['storagebox_name'],
                    'missing': None,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The values to update were invalid (storagebox_name)'

    def test_change_name(self, mocker):
        updated = legacy_update_info(23, name='Backup')
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_LEGACY_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json(updated)
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        for key in STORAGEBOX_LEGACY_KEYS:
            assert result[key] == updated['storagebox'][key], "Unexpected difference for {0!r}".format(key)

    def test_change_name_rate_limit_fail(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
            'rate_limit_retry_timeout': 0,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_LEGACY_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'interval': 5,
                    'max_request': 1,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['msg'] == (
            'Request failed: 403 RATE_LIMIT_EXCEEDED (Rate limit exceeded).'
            ' Maximum allowed requests: 1. Time interval in seconds: 5'
        )

    def test_change_name_rate_limit(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        updated = legacy_update_info(23, name='Backup')
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
            'rate_limit_retry_timeout': -1,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_LEGACY_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'interval': 5,
                    'max_request': 1,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'interval': 3,
                    'max_request': 1,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'interval': 4,
                    'max_request': 1,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json(updated)
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        for key in STORAGEBOX_LEGACY_KEYS:
            assert result[key] == updated['storagebox'][key], "Unexpected difference for {0!r}".format(key)
        sleep_mock.assert_has_calls([
            call(5),
            call(3),
            call(3),
            call(3),
        ])

    def test_change_name_rate_limit_timeout(self, mocker):
        elapsed = [123.4]

        def sleep(duration):
            elapsed[0] += duration
            print('sleep', duration, '->', elapsed[0])

        def get_time():
            elapsed[0] += 0.03
            print('get', elapsed[0])
            return elapsed[0]

        mocker.patch('time.sleep', sleep)
        mocker.patch('time.time', get_time)
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
            'rate_limit_retry_timeout': 7,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_LEGACY_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'interval': 5,
                    'max_request': 1,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'interval': 5,
                    'max_request': 1,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 403)
            .result_json({
                'error': {
                    'status': 403,
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded',
                    'interval': 5,
                    'max_request': 1,
                },
            })
            .expect_form_value('storagebox_name', 'Backup')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value_absent('ssh')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['msg'] == (
            'Request failed: 403 RATE_LIMIT_EXCEEDED (Rate limit exceeded).'
            ' Maximum allowed requests: 1. Time interval in seconds: 5.'
            ' Waited a total of 5.1 seconds for rate limit errors to go away'
        )

    def test_change_ssh(self, mocker):
        updated = legacy_update_info(23, ssh=False)
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 23,
            'name': 'Backup Server 2',
            'ssh': False,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(STORAGEBOX_LEGACY_DETAIL_DATA[23])
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json(updated)
            .expect_form_value_absent('storagebox_name')
            .expect_form_value_absent('webdav')
            .expect_form_value_absent('samba')
            .expect_form_value('ssh', 'false')
            .expect_form_value_absent('external_reachability')
            .expect_form_value_absent('zfs')
            .expect_url('{0}/storagebox/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        for key in STORAGEBOX_LEGACY_KEYS:
            assert result[key] == updated['storagebox'][key], "Unexpected difference for {0!r}".format(key)


class TestHetznerStoragebox(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_idempotent(self, mocker):
        updated = update_info(23)
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_token': 'asdf',
            'id': 23,
            'name': 'Backup Server 2',
            'webdav': False,
            'samba': False,
            'ssh': True,
            'external_reachability': True,
        }, [
            FetchUrlCall('GET', 200)
            .expect_header("Authorization", "Bearer asdf")
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['changed'] is False
        for key, keys in STORAGEBOX_KEYS.items():
            assert result[key] == get_key(updated['storage_box'], keys), "Unexpected difference for {0!r}".format(key)

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_token': '',
            'id': 1,
        }, [
            FetchUrlCall('GET', 404)
            .expect_header("Authorization", "Bearer ")
            .result_json({
                'error': {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                },
            })
            .expect_url('{0}/v1/storage_boxes/1'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Storagebox with ID 1 does not exist'

    def test_invalid_input(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 400)
            .result_json({
                'error': {
                    'code': 'invalid_input',
                    'message': "invalid input in field 'name': is too long",
                    'details': {
                        'fields': [
                            {
                                'name': 'name',
                                'message': 'is too long',
                            },
                        ],
                    },
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'The values to update were invalid (name: is too long)'

    def test_change_name(self, mocker):
        updated = update_info(23, name='Backup')
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 200)
            .result_json(updated)
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True
        for key, keys in STORAGEBOX_KEYS.items():
            assert result[key] == get_key(updated['storage_box'], keys), "Unexpected difference for {0!r}".format(key)

    def test_change_name_rate_limit_fail(self, mocker):
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
            'rate_limit_retry_timeout': 0,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Request failed: [rate_limit_exceeded] Rate limit exceeded'

    def test_change_name_rate_limit(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        updated = update_info(23, name='Backup')
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
            'rate_limit_retry_timeout': -1,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 200)
            .result_json(updated)
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True
        for key, keys in STORAGEBOX_KEYS.items():
            assert result[key] == get_key(updated['storage_box'], keys), "Unexpected difference for {0!r}".format(key)
        sleep_mock.assert_has_calls([
            call(5),
            call(5),
            call(5),
            call(5),
        ])

    def test_change_name_rate_limit_timeout(self, mocker):
        elapsed = [123.4]

        def sleep(duration):
            elapsed[0] += duration
            print('sleep', duration, '->', elapsed[0])

        def get_time():
            elapsed[0] += 0.03
            print('get', elapsed[0])
            return elapsed[0]

        mocker.patch('time.sleep', sleep)
        mocker.patch('time.time', get_time)
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup',
            'ssh': True,
            'rate_limit_retry_timeout': 7,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 429)
            .result_json({
                'error': {
                    'code': 'rate_limit_exceeded',
                    'message': 'Rate limit exceeded',
                    'details': {},
                },
            })
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Request failed: [rate_limit_exceeded] Rate limit exceeded'

    def test_change_ssh(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        updated = update_info(23, ssh=False)
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'ssh': False,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
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
            .expect_json_value_absent(['name'])
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value(['ssh_enabled'], False)
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23/actions/update_access_settings'.format(API_BASE_URL)),
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
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True
        for key, keys in STORAGEBOX_KEYS.items():
            assert result[key] == get_key(updated['storage_box'], keys), "Unexpected difference for {0!r}".format(key)
        sleep_mock.assert_has_calls([
            call(1),
        ])

    def test_change_ssh_fail(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup Server 2',
            'ssh': False,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
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
            .expect_json_value_absent(['name'])
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value(['ssh_enabled'], False)
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23/actions/update_access_settings'.format(API_BASE_URL)),
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
                    ],
                    "error": {
                        "code": "action_failed",
                        "message": "Action failed",
                    },
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Error while updating access settings: [action_failed] Action failed'
        sleep_mock.assert_has_calls([
            call(1),
        ])

    def test_change_ssh_fail_unknown(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup Server 2',
            'ssh': False,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
                    "status": "error",
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
            .expect_json_value_absent(['name'])
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value(['ssh_enabled'], False)
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23/actions/update_access_settings'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Error while updating access settings: Unknown error'
        sleep_mock.assert_has_calls([])

    def test_change_ssh_timeout(self, mocker):
        elapsed = [123.4]

        def sleep(duration):
            elapsed[0] += duration
            print('sleep', duration, '->', elapsed[0])

        def get_time():
            elapsed[0] += 0.03
            print('get', elapsed[0])
            return elapsed[0]

        mocker.patch('time.sleep', sleep)
        mocker.patch('time.time', get_time)
        updated = update_info(23, ssh=False)
        unfinished_action = {
            "action": {
                "id": 13,
                "command": "update_access_settings",
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
        }
        http_calls = [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json(unfinished_action)
            .expect_json_value_absent(['name'])
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value(['ssh_enabled'], False)
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23/actions/update_access_settings'.format(API_BASE_URL)),
        ]
        for i in range(57):
            http_calls.append(
                FetchUrlCall('GET', 200)
                .result_json(unfinished_action)
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL))
            )
        result = self.run_module_failed(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'ssh': False,
        }, http_calls)
        assert result['msg'] == 'Error while updating access settings: Timeout'

    def test_change_name_and_ssh(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        updated = update_info(23, ssh=False, name="Backup")
        updated_int = update_info(23, name="Backup")
        result = self.run_module_success(mocker, storagebox, {
            'hetzner_token': '',
            'id': 23,
            'name': 'Backup',
            'ssh': False,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({'storage_box': STORAGEBOX_DETAIL_DATA[23]})
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('PUT', 200)
            .result_json(updated_int)
            .expect_json_value(['name'], 'Backup')
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value_absent(['ssh_enabled'])
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
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
            .expect_json_value_absent(['name'])
            .expect_json_value_absent(['access_settings'])
            .expect_json_value_absent(['webdav_enabled'])
            .expect_json_value_absent(['samba_enabled'])
            .expect_json_value(['ssh_enabled'], False)
            .expect_json_value_absent(['zfs_enabled'])
            .expect_url('{0}/v1/storage_boxes/23/actions/update_access_settings'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "update_access_settings",
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
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
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
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])
        assert result['changed'] is True
        for key, keys in STORAGEBOX_KEYS.items():
            assert result[key] == get_key(updated['storage_box'], keys), "Unexpected difference for {0!r}".format(key)
        sleep_mock.assert_has_calls([
            call(1),
            call(1),
        ])
