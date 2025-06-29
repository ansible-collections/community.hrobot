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
from ansible_collections.community.hrobot.plugins.modules import storagebox_set_password

RANDOM_PASSWORD = 'randompassword'


class TestStorageboxSetPasswordLegacy(BaseTestModule):

    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_set_password.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_specific_password(self, mocker):
        result = self.run_module_success(mocker, storagebox_set_password, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 123,
            'password': 'newpassword'
        }, [
            FetchUrlCall("POST", 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_form_value('password', 'newpassword')
            .result_json({'password': 'newpassword'})
            .expect_url(BASE_URL + '/storagebox/123/password'),
        ])
        assert result['changed'] is True
        assert result['password'] == 'newpassword'

    def test_random_password(self, mocker):
        result = self.run_module_success(mocker, storagebox_set_password, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 123,
        }, [
            FetchUrlCall("POST", 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_form_value_absent('password')
            .result_json({'password': RANDOM_PASSWORD})
            .expect_url(BASE_URL + '/storagebox/123/password'),
        ])
        assert result['changed'] is True
        assert result['password'] == RANDOM_PASSWORD

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_set_password, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 456,
        }, [FetchUrlCall("POST", 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storage Box with ID 456 not found',
                },
            })
            .expect_url(BASE_URL + '/storagebox/456/password'),
            ])
        assert result['msg'] == 'Storage Box with ID 456 not found'

    def test_password_invalid(self, mocker):
        result = self.run_module_failed(mocker, storagebox_set_password, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'id': 123,
            'password': 'invalidpassword',
        }, [
            FetchUrlCall("POST", 409)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json({
                'error': {
                    'status': 409,
                    'code': 'STORAGEBOX_INVALID_PASSWORD',
                    'message': "The chosen password has been considered insecure or does not comply with Hetzner's password guideline",
                }})
            .expect_url(BASE_URL + '/storagebox/123/password')
        ])
        assert result['msg'] == "The chosen password has been considered insecure or does not comply with Hetzner's password guideline"


class TestStorageboxSetPassword(BaseTestModule):

    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_set_password.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_specific_password(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_set_password, {
            'hetzner_token': 'asdf',
            'id': 123,
            'password': 'newpassword'
        }, [
            FetchUrlCall("POST", 200)
            .expect_json_value(['password'], 'newpassword')
            .result_json({
                "action": {
                    "id": 13,
                    "command": "reset_password",
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
            .expect_url('{0}/v1/storage_boxes/123/actions/reset_password'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "reset_password",
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
        assert result['password'] == 'newpassword'

    def test_specific_password_failed(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox_set_password, {
            'hetzner_token': 'asdf',
            'id': 123,
            'password': 'newpassword'
        }, [
            FetchUrlCall("POST", 200)
            .expect_json_value(['password'], 'newpassword')
            .result_json({
                "action": {
                    "id": 13,
                    "command": "reset_password",
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
            .expect_url('{0}/v1/storage_boxes/123/actions/reset_password'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "reset_password",
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
        assert result['msg'] == "Error while resetting password: [action_failed] Action failed"

    def test_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_set_password, {
            'hetzner_token': 'asdf',
            'id': 456,
            'password': 'newpassword'
        }, [
            FetchUrlCall("POST", 404)
            .expect_json_value(['password'], 'newpassword')
            .result_json({
                'error': {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                },
            })
            .expect_url('{0}/v1/storage_boxes/456/actions/reset_password'.format(API_BASE_URL)),
        ])
        assert result['msg'] == 'Storage Box with ID 456 not found'
