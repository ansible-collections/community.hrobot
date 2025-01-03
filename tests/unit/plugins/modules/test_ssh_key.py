# Copyright (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import ssh_key


# Key generated with `ssh-keygen -t rsa -b 4096 -f test`, fingerprint with `ssh-keygen -lf test.pub -E md5``
PUBLIC_KEY_1 = (
    'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC7g+C+gXspRfsNRFXHSeEuQLrUEb+pSV9OUi3zz0DvdxzaXyP4I1vUErnwll5P5'
    '8KFdkWp65haqiGteM53zuGJa251c+J41Y69jLEI0jX4mGj4BskB0Cud23lnVzYTktzjkwGz2tGlRjaSYzYdm9lR3Nf6rlWBP1iz6C'
    'QasBHVLGWUBuJF+DQ16ztHV9EWtifDprVoMHK5EaGW19W5OCW73sPJfvbdDjolTZC6QZ7lKOGcZjdFBM7nnIyfIHYfjnXPZh9eMnY'
    '6KWEAKuhQpPO1SB82PrLvBPlYzNewO1BiOQWoJyJfJBr1vRBfhLzY9VAoNr5fDSUxtn3UmZ2OmcNCx+qb8iUrn+E3K3i4sRn5iYVA'
    'dO4pmsjx5SENXlfpj/Mmz6wu3bQGN5k1jYtq+sKxGuIRiX+9sxEQ1KBXIqMfM1zSzitxGQSGUrqEgWpxJKVmDscGnlZBGGTPvPRwX'
    'i3VLeiTH+AkGOnWrlVenKpBh/0IWPI8fN/d7GolWHT53Cyi0HQbb3nKMUlfXWFKukbdSb9mvJ0v1Pv8qlWb6+fDZCBi0hz/fmE+hx'
    '/+uwnY9Vk8H5CzTDQOmXKx6Gj3Lff9RSWD/WePW8LyukWz0l18GOGWzv/HqNIVtljdfJMa5v2kckhZAFPxQvZBMUIX0wkRTmGJOcQ'
    '+A8ZKOVaScMnXXQ=='
)
FINGERPRINT_1 = 'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0'
TYPE_1 = 'RSA'
SIZE_1 = 4096


class TestHetznerSSHKey(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.ssh_key.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    # Absent with fingerprint

    def test_absent_fp(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'state': 'absent',
            'fingerprint': FINGERPRINT_1,
        }, [
            FetchUrlCall('DELETE', 200)
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    def test_absent_fp_idempotent(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'absent',
            'fingerprint': FINGERPRINT_1,
        }, [
            FetchUrlCall('DELETE', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'Key not found',
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is False
        assert result['fingerprint'] == FINGERPRINT_1

    def test_absent_fp_check_mode(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'absent',
            'fingerprint': FINGERPRINT_1,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'key': {
                    'name': 'My Test Key',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    def test_absent_fp_idempotent_check_mode(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'absent',
            'fingerprint': FINGERPRINT_1,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'Key not found',
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is False
        assert result['fingerprint'] == FINGERPRINT_1

    # Absent with public key

    def test_absent_key(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'absent',
            'public_key': PUBLIC_KEY_1,
        }, [
            FetchUrlCall('DELETE', 200)
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    def test_absent_key_idempotent(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'absent',
            'public_key': PUBLIC_KEY_1,
        }, [
            FetchUrlCall('DELETE', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'Key not found',
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is False
        assert result['fingerprint'] == FINGERPRINT_1

    def test_absent_key_check_mode(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'absent',
            'public_key': PUBLIC_KEY_1,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'key': {
                    'name': 'My Test Key',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    def test_absent_key_idempotent_check_mode(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'absent',
            'public_key': PUBLIC_KEY_1,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'Key not found',
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is False
        assert result['fingerprint'] == FINGERPRINT_1

    # Present

    def test_present_create_check_mode(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'present',
            'name': 'foo',
            'public_key': PUBLIC_KEY_1,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'Key not found',
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    def test_present_create(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'present',
            'name': 'foo',
            'public_key': PUBLIC_KEY_1,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'NOT_FOUND',
                    'message': 'Key not found',
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
            FetchUrlCall('POST', 200)
            .expect_form_value('name', 'foo')
            .expect_form_value('data', PUBLIC_KEY_1)
            .result_json({
                'key': {
                    'name': 'foo',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    def test_present_idempotent_check_mode(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'present',
            'name': 'foo',
            'public_key': PUBLIC_KEY_1,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'key': {
                    'name': 'foo',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is False
        assert result['fingerprint'] == FINGERPRINT_1

    def test_present_idempotent(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'present',
            'name': 'foo',
            'public_key': PUBLIC_KEY_1,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'key': {
                    'name': 'foo',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is False
        assert result['fingerprint'] == FINGERPRINT_1

    def test_present_change_check_mode(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'present',
            'name': 'bar',
            'public_key': PUBLIC_KEY_1,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'key': {
                    'name': 'foo',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    def test_present_change(self, mocker):
        result = self.run_module_success(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'present',
            'name': 'bar',
            'public_key': PUBLIC_KEY_1,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                'key': {
                    'name': 'foo',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
            FetchUrlCall('POST', 200)
            .expect_form_value('name', 'bar')
            .expect_form_value_absent('data')
            .result_json({
                'key': {
                    'name': 'bar',
                    'fingerprint': FINGERPRINT_1,
                    'type': TYPE_1,
                    'size': SIZE_1,
                    'data': PUBLIC_KEY_1,
                },
            })
            .expect_url('{0}/key/{1}'.format(BASE_URL, FINGERPRINT_1)),
        ])
        assert result['changed'] is True
        assert result['fingerprint'] == FINGERPRINT_1

    # Error

    def test_invalid_public_key(self, mocker):
        result = self.run_module_failed(mocker, ssh_key, {
            'hetzner_user': '',
            'hetzner_password': '',
            'state': 'present',
            'name': 'bar',
            'public_key': 'asdf',
        }, [])
        assert result['msg'] == 'Error while extracting fingerprint from public key data: cannot split public key into at least two parts'
