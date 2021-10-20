# (c) 2019 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import reverse_dns


class TestHetznerReverseDNS(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.reverse_dns.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_idempotent_present(self, mocker):
        result = self.run_module_success(mocker, reverse_dns, {
            'hetzner_user': '',
            'hetzner_password': '',
            'ip': '1.2.3.4',
            'value': 'foo.example.com',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'rdns': {
                    'ip': '1.2.3.4',
                    'ptr': 'foo.example.com',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False

    def test_idempotent_absent(self, mocker):
        result = self.run_module_success(mocker, reverse_dns, {
            'hetzner_user': '',
            'hetzner_password': '',
            'ip': '1.2.3.4',
            'state': 'absent',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'RDNS_NOT_FOUND',
                    'message': 'The IP address 1.2.3.4 has no reverse DNS entry yet',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is False

    def test_set_check_mode(self, mocker):
        result = self.run_module_success(mocker, reverse_dns, {
            'hetzner_user': '',
            'hetzner_password': '',
            'ip': '1.2.3.4',
            'value': 'foo.example.com',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'RDNS_NOT_FOUND',
                    'message': 'The IP address 1.2.3.4 has no reverse DNS entry yet',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True

    def test_set(self, mocker):
        result = self.run_module_success(mocker, reverse_dns, {
            'hetzner_user': '',
            'hetzner_password': '',
            'ip': '1.2.3.4',
            'value': 'foo.example.com',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'RDNS_NOT_FOUND',
                    'message': 'The IP address 1.2.3.4 has no reverse DNS entry yet',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
            FetchUrlCall('POST', 201)
            .expect_form_value('ptr', 'foo.example.com')
            .result_json({
                'rdns': {
                    'ip': '1.2.3.4',
                    'ptr': 'foo.example.com',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True

    def test_remove_check_mode(self, mocker):
        result = self.run_module_success(mocker, reverse_dns, {
            'hetzner_user': '',
            'hetzner_password': '',
            'ip': '1.2.3.4',
            'state': 'absent',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'rdns': {
                    'ip': '1.2.3.4',
                    'ptr': 'foo.example.com',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True

    def test_remove(self, mocker):
        result = self.run_module_success(mocker, reverse_dns, {
            'hetzner_user': '',
            'hetzner_password': '',
            'ip': '1.2.3.4',
            'state': 'absent',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'rdns': {
                    'ip': '1.2.3.4',
                    'ptr': 'foo.example.com',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['changed'] is True

    def test_bad_ip(self, mocker):
        result = self.run_module_failed(mocker, reverse_dns, {
            'hetzner_user': '',
            'hetzner_password': '',
            'ip': '1.2.3.4',
            'value': 'foo.example.com',
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'IP_NOT_FOUND',
                    'message': 'The IP address 1.2.3.4 was not found',
                },
            })
            .expect_url('{0}/rdns/1.2.3.4'.format(BASE_URL)),
        ])
        assert result['msg'] == 'The IP address was not found'
