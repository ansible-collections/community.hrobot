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
from ansible_collections.community.hrobot.plugins.modules import server


def create_server_data(server_name):
    return {
        'server': {
            'cancelled': False,
            'cpanel': False,
            'dc': 'NBG1-DC1',
            'hot_swap': True,
            'ip': [
                '1.2.3.4',
            ],
            'linked_storagebox': None,
            'paid_until': '2021-12-31',
            'plesk': False,
            'product': 'EX41',
            'rescue': True,
            'reset': True,
            'server_ip': '1.2.3.4',
            'server_ipv6_net': '2a01:1:2:3::',
            'server_name': server_name,
            'server_number': 23,
            'status': 'ready',
            'subnet': [
                {
                    'ip': '2a01:1:2:3::',
                    'mask': '64',
                },
            ],
            'traffic': 'unlimited',
            'vnc': True,
            'windows': False,
            'wol': True,
        },
    }


class TestHetznerServer(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.server.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_idempotent_not_specified(self, mocker):
        result = self.run_module_success(mocker, server, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'server_number': 23,
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json(create_server_data('foo'))
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['server'] == create_server_data('foo')['server']

    def test_idempotent(self, mocker):
        result = self.run_module_success(mocker, server, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'server_name': 'foo',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(create_server_data('foo'))
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['server'] == create_server_data('foo')['server']

    def test_change_check_mode(self, mocker):
        result = self.run_module_success(mocker, server, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'server_name': 'bar',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(create_server_data('foo'))
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['server'] == create_server_data('bar')['server']

    def test_change(self, mocker):
        result = self.run_module_success(mocker, server, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'server_name': 'bar',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(create_server_data('foo'))
            .expect_url('{0}/server/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .expect_form_value('server_name', 'bar')
            .result_json(create_server_data('bar'))
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['server'] == create_server_data('bar')['server']

    # Errors

    def test_server_not_found(self, mocker):
        result = self.run_module_failed(mocker, server, {
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
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'This server does not exist, or you do not have access rights for it'

    def test_invalid_input(self, mocker):
        result = self.run_module_failed(mocker, server, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'server_name': 'bar',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(create_server_data('foo'))
            .expect_url('{0}/server/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .expect_form_value('server_name', 'bar')
            .result_json({
                'error': {
                    'status': 400,
                    'code': 'INVALID_INPUT',
                    'message': 'Invalid input parameters',
                },
            })
            .expect_url('{0}/server/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The values to update were invalid ({"server_name": "bar"})'
