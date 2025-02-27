# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import reset_info


class TestHetznerResetInfo(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.reset_info.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_valid(self, mocker):
        result = self.run_module_success(mocker, reset_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'server_number': 23,
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
                        'man',
                    ],
                    'operating_status': 'not supported',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['reset'] == {
            'server_ip': '123.123.123.123',
            'server_ipv6_net': '2a01:4f8:111:4221::',
            'server_number': 23,
            'type': [
                'software',
                'hardware',
                'manual',
            ],
            'operating_status': 'not supported',
        }

    def test_valid_no_type(self, mocker):
        result = self.run_module_success(mocker, reset_info, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'server_number': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json({
                'reset': {
                    'server_ip': '123.123.123.123',
                    'server_ipv6_net': '2a01:4f8:111:4221::',
                    'server_number': 23,
                    'operating_status': 'not supported',
                },
            })
            .expect_url('{0}/reset/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['reset'] == {
            'server_ip': '123.123.123.123',
            'server_ipv6_net': '2a01:4f8:111:4221::',
            'server_number': 23,
            'operating_status': 'not supported',
        }

    # Errors

    def test_server_not_found(self, mocker):
        result = self.run_module_failed(mocker, reset_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
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
        result = self.run_module_failed(mocker, reset_info, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
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
