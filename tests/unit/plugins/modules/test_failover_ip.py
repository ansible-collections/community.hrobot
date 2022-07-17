# Copyright (c) 2020 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import failover_ip


class TestHetznerFailoverIP(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.failover_ip.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    # Tests for state idempotence (routed and unrouted)

    def test_unrouted(self, mocker):
        result = self.run_module_success(mocker, failover_ip, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'failover_ip': '1.2.3.4',
            'state': 'unrouted',
        }, [
            FetchUrlCall('GET', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': None,
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['value'] is None
        assert result['state'] == 'unrouted'

    def test_routed(self, mocker):
        result = self.run_module_success(mocker, failover_ip, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
            'state': 'routed',
            'value': '4.3.2.1',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '4.3.2.1',
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['value'] == '4.3.2.1'
        assert result['state'] == 'routed'

    # Tests for changing state (unrouted to routed, vice versa)

    def test_unrouted_to_routed(self, mocker):
        result = self.run_module_success(mocker, failover_ip, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
            'state': 'routed',
            'value': '4.3.2.1',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': None,
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '4.3.2.1',
                },
            })
            .expect_form_value('active_server_ip', '4.3.2.1')
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['value'] == '4.3.2.1'
        assert result['state'] == 'routed'

    def test_unrouted_to_routed_check_mode(self, mocker):
        result = self.run_module_success(mocker, failover_ip, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
            'state': 'routed',
            'value': '4.3.2.1',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': None,
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['value'] == '4.3.2.1'
        assert result['state'] == 'routed'

    def test_routed_to_unrouted(self, mocker):
        result = self.run_module_success(mocker, failover_ip, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
            'state': 'unrouted',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '4.3.2.1',
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': None,
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['value'] is None
        assert result['state'] == 'unrouted'

    # Tests for re-routing

    def test_rerouting(self, mocker):
        result = self.run_module_success(mocker, failover_ip, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
            'state': 'routed',
            'value': '4.3.2.1',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '5.4.3.2',
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '4.3.2.1',
                },
            })
            .expect_form_value('active_server_ip', '4.3.2.1')
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['value'] == '4.3.2.1'
        assert result['state'] == 'routed'

    def test_rerouting_already_routed(self, mocker):
        result = self.run_module_success(mocker, failover_ip, {
            'hetzner_user': '',
            'hetzner_password': '',
            'failover_ip': '1.2.3.4',
            'state': 'routed',
            'value': '4.3.2.1',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '5.4.3.2',
                },
            })
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
            FetchUrlCall('POST', 409)
            .result_json({
                'error': {
                    'status': 409,
                    'code': 'FAILOVER_ALREADY_ROUTED',
                    'message': 'Failover already routed',
                },
                'failover': {
                    'ip': '1.2.3.4',
                    'netmask': '255.255.255.255',
                    'server_ip': '2.3.4.5',
                    'server_number': 2345,
                    'active_server_ip': '4.3.2.1',
                },
            })
            .expect_form_value('active_server_ip', '4.3.2.1')
            .expect_url('{0}/failover/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['value'] == '4.3.2.1'
        assert result['state'] == 'routed'
