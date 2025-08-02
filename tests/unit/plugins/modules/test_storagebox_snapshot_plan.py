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
from ansible_collections.community.hrobot.plugins.modules import storagebox_snapshot_plan


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
            'max_snapshots': 2,
            'minute': 5,
            'hour': 12,
            'day_of_week': 2,
            'day_of_month': None,
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


class TestHetznerStorageboxSnapshotPlanLegacy(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot_plan.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1,
            'plans': [
                {
                    'status': 'enabled',
                    'minute': 5,
                    'hour': 12,
                    'day_of_week': 2,
                    'day_of_month': None,
                    'month': None,
                    'max_snapshots': 2,
                },
            ],
        }, [
        ])
        assert result['msg'] == 'Storagebox with ID 1 does not exist'


class TestHetznerStorageboxSnapshotPlan(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_snapshot_plan.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_idempotent(self, mocker):
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_token': 'asdf',
            'storagebox_id': 23,
            'plans': [
                {
                    'status': 'enabled',
                    'minute': 5,
                    'hour': 12,
                    'day_of_week': 2,
                    'day_of_month': None,
                    'month': None,
                    'max_snapshots': 2,
                }
            ],
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
            'minute': 5,
            'hour': 12,
            'day_of_week': 2,
            'day_of_month': None,
            'month': None,
            'max_snapshots': 2,
        }

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
            'storagebox_id': 1,
            'plans': [
                {
                    'status': 'enabled',
                    'minute': 5,
                    'hour': 12,
                    'day_of_week': 2,
                    'day_of_month': None,
                    'month': None,
                    'max_snapshots': 2,
                }
            ],
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
        assert result['msg'] == 'Storagebox with ID 1 does not exist'

    def test_wrong_number_of_plans(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'plans': [],
        }, [
        ])
        assert result['msg'] == '`plans` must have exactly one element'

    def test_month(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'plans': [
                {
                    'status': 'enabled',
                    'minute': 5,
                    'hour': 12,
                    'day_of_week': 2,
                    'day_of_month': None,
                    'month': 2,
                    'max_snapshots': 2,
                }
            ],
        }, [
        ])
        assert result['msg'] == 'The new Hetzner API does not support specifying month for a plan.'

    def test_invalid_input(self, mocker):
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
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
            .result_json(STORAGEBOX_PLAN_ENABLED)
            .expect_url('{0}/v1/storage_boxes/23'.format(API_BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json({
                "error": {
                    'code': 'invalid_input',
                    'message': 'invalid input in field hour',
                    'details': {
                        'fields': [
                            {
                                'name': 'hour',
                                'messages': ['This value should be between 0 and 23.'],
                            },
                        ],
                    },
                },
            })
            .expect_json_value_absent(['status'])
            .expect_json_value_absent(['month'])
            .expect_json_value(['minute'], 0)
            .expect_json_value(['hour'], 25)
            .expect_json_value(['max_snapshots'], -1)
            .expect_json_value(['day_of_week'], None)
            .expect_json_value(['day_of_month'], None)
            .expect_url('{0}/v1/storage_boxes/23/actions/enable_snapshot_plan'.format(API_BASE_URL)),
        ])
        assert result['msg'] in (
            # Python 3.6+:
            "Request failed: [invalid_input] invalid input in field hour. Details:"
            " {'fields': [{'name': 'hour', 'messages': ['This value should be between 0 and 23.']}]}",
            # Python 3.5 can have this too:
            "Request failed: [invalid_input] invalid input in field hour. Details:"
            " {'fields': [{'messages': ['This value should be between 0 and 23.'], 'name': 'hour'}]}",
            # These are Python 2.7:
            "Request failed: [invalid_input] invalid input in field hour. Details:"
            " {u'fields': [{u'name': u'hour', u'messages': [u'This value should be between 0 and 23.']}]}",
            "Request failed: [invalid_input] invalid input in field hour. Details:"
            " {u'fields': [{u'messages': [u'This value should be between 0 and 23.'], u'name': u'hour'}]}",
        )

    def test_disable(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
            'storagebox_id': 23,
            'plans': [
                {
                    'status': 'disabled',
                },
            ],
        }, [
            FetchUrlCall('GET', 200)
            .result_json(STORAGEBOX_PLAN_ENABLED)
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
            .expect_header_unset('Content-Type')
            .expect_content_predicate(lambda data: data is None)
            .expect_url('{0}/v1/storage_boxes/23/actions/disable_snapshot_plan'.format(API_BASE_URL)),
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
        assert len(result['plans']) == 1
        assert result['plans'][0] == {
            'status': 'disabled',
            'minute': None,
            'hour': None,
            'day_of_week': None,
            'day_of_month': None,
            'month': None,
            'max_snapshots': None,
        }

    def test_enable(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
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
            .result_json(STORAGEBOX_PLAN_DISABLED)
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
            .expect_json_value_absent(['status'])
            .expect_json_value_absent(['month'])
            .expect_json_value(['minute'], 5)
            .expect_json_value(['hour'], 12)
            .expect_json_value(['max_snapshots'], 2)
            .expect_json_value(['day_of_week'], 2)
            .expect_json_value(['day_of_month'], None)
            .expect_header('Content-Type', 'application/json')
            .expect_url('{0}/v1/storage_boxes/23/actions/enable_snapshot_plan'.format(API_BASE_URL)),
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
        assert len(result['plans']) == 1
        assert result['plans'][0] == {
            'status': 'enabled',
            'minute': 5,
            'hour': 12,
            'day_of_week': 2,
            'day_of_month': None,
            'month': None,
            'max_snapshots': 2,
        }

    def test_change(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
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
            .result_json(STORAGEBOX_PLAN_ENABLED)
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
            .expect_json_value_absent(['status'])
            .expect_json_value_absent(['month'])
            .expect_json_value(['minute'], 5)
            .expect_json_value(['hour'], 12)
            .expect_json_value(['max_snapshots'], 2)
            .expect_json_value(['day_of_week'], None)
            .expect_json_value(['day_of_month'], 1)
            .expect_header('Content-Type', 'application/json')
            .expect_url('{0}/v1/storage_boxes/23/actions/enable_snapshot_plan'.format(API_BASE_URL)),
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
        assert len(result['plans']) == 1
        assert result['plans'][0] == {
            'status': 'enabled',
            'minute': 5,
            'hour': 12,
            'day_of_week': None,
            'day_of_month': 1,
            'month': None,
            'max_snapshots': 2,
        }

    def test_change_fail(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox_snapshot_plan, {
            'hetzner_token': '',
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
            .result_json(STORAGEBOX_PLAN_ENABLED)
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
            .expect_json_value_absent(['status'])
            .expect_json_value_absent(['month'])
            .expect_json_value(['minute'], 5)
            .expect_json_value(['hour'], 12)
            .expect_json_value(['max_snapshots'], 2)
            .expect_json_value(['day_of_week'], None)
            .expect_json_value(['day_of_month'], 1)
            .expect_header('Content-Type', 'application/json')
            .expect_url('{0}/v1/storage_boxes/23/actions/enable_snapshot_plan'.format(API_BASE_URL)),
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
        assert result['msg'] == 'Error while updating the snapshot plan: [action_failed] Action failed'
