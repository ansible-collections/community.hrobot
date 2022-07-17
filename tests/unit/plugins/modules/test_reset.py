# Copyright (c) 2019 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import reset


class TestHetznerReset(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.reset.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_check_valid(self, mocker):
        result = self.run_module_success(mocker, reset, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'server_number': 23,
            'reset_type': 'software',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json({
                'reset': {
                    'server_ip': '123.123.123.123',
                    'server_ipv6_net': '2a01:4f8:111:4221::',
                    'server_number': 23,
                    'type': [
                        'sw',
                        'hw',
                        'man'
                    ],
                    'operating_status': 'not supported',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True

    def test_valid(self, mocker):
        result = self.run_module_success(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'manual',
        }, [
            FetchUrlCall('POST', 200)
            .expect_form_value('type', 'man')
            .result_json({
                'reset': {
                    'server_ip': '123.123.123.123',
                    'server_ipv6_net': '2a01:4f8:111:4221::',
                    'server_number': 23,
                    'type': 'man',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True

    # Errors

    def test_invalid(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
        }, [
            FetchUrlCall('POST', 400)
            .expect_form_value('type', 'power')
            .result_json({
                'error': {
                    'status': 400,
                    'code': 'INVALID_INPUT',
                    'message': 'Invalid input parameters',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The chosen reset method is not supported for this server'

    def test_check_invalid(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'reset': {
                    'server_ip': '123.123.123.123',
                    'server_ipv6_net': '2a01:4f8:111:4221::',
                    'server_number': 23,
                    'type': [
                        'sw',
                        'hw',
                        'man'
                    ],
                    'operating_status': 'not supported',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The chosen reset method is not supported for this server'

    def test_server_not_found(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
        }, [
            FetchUrlCall('POST', 404)
            .expect_form_value('type', 'power')
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'SERVER_NOT_FOUND',
                    'message': 'Server not found',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'This server does not exist, or you do not have access rights for it'

    def test_check_server_not_found(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'SERVER_NOT_FOUND',
                    'message': 'Server not found',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'This server does not exist, or you do not have access rights for it'

    def test_reset_not_available(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
        }, [
            FetchUrlCall('POST', 404)
            .expect_form_value('type', 'power')
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'RESET_NOT_AVAILABLE',
                    'message': 'The server has no reset option',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The server has no reset option available'

    def test_check_reset_not_available(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'RESET_NOT_AVAILABLE',
                    'message': 'The server has no reset option',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The server has no reset option available'

    def test_reset_manual_active(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
        }, [
            FetchUrlCall('POST', 409)
            .expect_form_value('type', 'power')
            .result_json({
                'error': {
                    'status': 409,
                    'code': 'RESET_MANUAL_ACTIVE',
                    'message': 'There is already a running manual reset',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'A manual reset is already running'

    def test_reset_failed(self, mocker):
        result = self.run_module_failed(mocker, reset, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'reset_type': 'power',
        }, [
            FetchUrlCall('POST', 500)
            .expect_form_value('type', 'power')
            .result_json({
                'error': {
                    'status': 500,
                    'code': 'RESET_FAILED',
                    'message': 'Resetting failed due to an internal error',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The reset failed due to an internal error at Hetzner'
