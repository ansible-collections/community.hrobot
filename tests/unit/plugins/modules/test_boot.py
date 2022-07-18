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
from ansible_collections.community.hrobot.plugins.modules import boot


def _amend_server_data(data):
    data.update({
        'server_ip': '123.123.123.123',
        'server_ipv6_net': '2a01:4f8:111:4221::',
        'server_number': 23,
    })
    return data


def create_rescue_inactive():
    return _amend_server_data({
        'active': False,
        'arch': [64, 32],
        'authorized_key': [],
        'boot_time': None,
        'host_key': [],
        'os': ['linux', 'linuxold', 'freebsd', 'freebsdbeta', 'freebsdax', 'freebsdbetaax', 'vkvm', 'vkvmold'],
        'password': None,
    })


def create_rescue_active(os='linux', arch=64, authorized_key=None, host_key=None):
    return _amend_server_data({
        'active': True,
        'arch': arch,
        'authorized_key': authorized_key or [],
        'boot_time': None,
        'host_key': host_key or [],
        'os': os,
        'password': 'aBcDeFgHiJ1234',
    })


def create_linux_inactive():
    return {
        'dist': [
            'Arch Linux latest minimal',
            'CentOS 7.9 minimal',
            'CentOS 8.4 minimal',
            'Debian 10.10 LAMP',
            'Debian 10.10 minimal',
            'Debian 11 base',
            'Ubuntu 18.04.5 LTS minimal',
            'Ubuntu 18.04.5 LTS Nextcloud',
            'Ubuntu 20.04.1 LTS minimal',
        ],
        'arch': [64],
        'lang': ['en'],
        'active': False,
        'password': None,
        'authorized_key': [],
        'host_key': [],
    }


def create_linux_active(dist='Arch Linux latest minimal', arch=64, lang='en', authorized_key=None, host_key=None):
    return {
        'dist': dist,
        'arch': arch,
        'lang': lang,
        'active': True,
        'password': 'aBcDeFgHiJ1234',
        'authorized_key': authorized_key or [],
        'host_key': host_key or [],
    }


def create_vnc_inactive():
    return {
        'dist': ['CentOS-7.9', 'CentOS-8.4', 'Fedora-33', 'openSUSE-15.2'],
        'arch': [64],
        'lang': ['de_DE', 'en_US', 'fr_FR', 'ru_RU'],
        'active': False,
        'password': None,
    }


def _amend_boot(data=None):
    if data is None:
        data = {}
    if 'rescue' not in data:
        data['rescue'] = create_rescue_inactive()
    if 'linux' not in data:
        data['linux'] = create_linux_inactive()
    if 'vnc' not in data:
        data['vnc'] = create_vnc_inactive()
    for section in ('windows', 'plesk', 'cpanel'):
        if section not in data:
            data[section] = None
    return {
        'boot': data,
    }


class TestHetznerBoot(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.boot.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_idempotent_regular(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': 'test',
            'hetzner_password': 'hunter2',
            'server_number': 23,
            'regular_boot': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'rescue': create_linux_inactive(),
            }))
            .expect_basic_auth('test', 'hunter2')
            .expect_force_basic_auth(True)
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['configuration_type'] == 'regular_boot'
        assert result['password'] is None

    def test_rescue_idempotent(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'rescue': {
                'os': 'linux',
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'rescue': create_rescue_active(os='linux'),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['configuration_type'] == 'rescue'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_rescue_idempotent_2(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'rescue': {
                'os': 'linux',
                'arch': 32,
                'authorized_keys': [
                    'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0',
                    'aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99',
                    '0f:1e:2d:3c:4b:5a:69:78:87:96:a5:b4:c3:d2:e1:f0',
                ],
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'rescue': create_rescue_active(os='linux', arch=32, authorized_key=[
                    {
                        'key': {
                            'fingerprint': 'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0',
                            'name': 'baz',
                            'size': 4096,
                            'type': 'RSA',
                        },
                    },
                    {
                        'key': {
                            'fingerprint': 'aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99',
                            'name': 'foo bar',
                            'size': 2048,
                            'type': 'RSA',
                        },
                    },
                    {
                        'key': {
                            'fingerprint': '0f:1e:2d:3c:4b:5a:69:78:87:96:a5:b4:c3:d2:e1:f0',
                            'name': 'test',
                            'size': 3072,
                            'type': 'RSA',
                        },
                    },
                ]),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['configuration_type'] == 'rescue'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_rescue_deactivate(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'regular_boot': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'rescue': create_rescue_active(os='linux'),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .expect_url('{0}/boot/23/rescue'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'regular_boot'
        assert result['password'] is None

    def test_rescue_deactivate_check_mode(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'regular_boot': True,
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'rescue': create_rescue_active(os='linux'),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'regular_boot'
        assert result['password'] is None

    def test_rescue_activate(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'rescue': {
                'os': 'linux',
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot())
            .expect_url('{0}/boot/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .expect_form_value('os', 'linux')
            .expect_form_value_absent('arch')
            .expect_form_value_absent('authorized_key')
            .result_json({
                'rescue': create_rescue_active(os='linux'),
            })
            .expect_url('{0}/boot/23/rescue'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'rescue'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_rescue_activate_check_mode(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'rescue': {
                'os': 'linux',
            },
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot())
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'rescue'
        assert result['password'] is None

    def test_rescue_reactivate(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'rescue': {
                'os': 'linuxold',
                'arch': 32,
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'rescue': create_rescue_active(os='linux'),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .expect_url('{0}/boot/23/rescue'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .expect_form_value('os', 'linuxold')
            .expect_form_value('arch', '32')
            .expect_form_value_absent('authorized_key')
            .result_json({
                'rescue': create_rescue_active(os='linuxold', arch=32),
            })
            .expect_url('{0}/boot/23/rescue'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'rescue'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_rescue_reactivate_check_mode(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'rescue': {
                'os': 'linuxold',
                'arch': 32,
            },
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'rescue': create_rescue_active(os='linux'),
            }))
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'rescue'
        assert result['password'] is None

    def test_install_linux_idempotent(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'install_linux': {
                'dist': 'Arch Linux latest minimal',
                'lang': 'en',
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'linux': create_linux_active(dist='Arch Linux latest minimal', lang='en'),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['configuration_type'] == 'install_linux'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_install_linux_idempotent_2(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'install_linux': {
                'dist': 'Arch Linux latest minimal',
                'arch': 32,
                'lang': 'de',
                'authorized_keys': [
                    'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0',
                    '0f:1e:2d:3c:4b:5a:69:78:87:96:a5:b4:c3:d2:e1:f0',
                    'aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99',
                ],
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'linux': create_linux_active(dist='Arch Linux latest minimal', arch=32, lang='de', authorized_key=[
                    {
                        'key': {
                            'fingerprint': 'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0',
                            'name': 'abc',
                            'size': 4096,
                            'type': 'RSA',
                        },
                    },
                    {
                        'key': {
                            'fingerprint': 'aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99',
                            'name': 'buzz',
                            'size': 2048,
                            'type': 'RSA',
                        },
                    },
                    {
                        'key': {
                            'fingerprint': '0f:1e:2d:3c:4b:5a:69:78:87:96:a5:b4:c3:d2:e1:f0',
                            'name': 'afz',
                            'size': 2048,
                            'type': 'RSA',
                        },
                    },
                ]),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['changed'] is False
        assert result['configuration_type'] == 'install_linux'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_install_linux_deactivate(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'regular_boot': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'linux': create_linux_active(dist='Arch Linux latest minimal'),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .expect_url('{0}/boot/23/linux'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'regular_boot'
        assert result['password'] is None

    def test_install_linux_activate(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'install_linux': {
                'dist': 'Arch Linux latest minimal',
                'lang': 'en',
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot())
            .expect_url('{0}/boot/23'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .expect_form_value('dist', 'Arch Linux latest minimal')
            .expect_form_value_absent('arch')
            .expect_form_value_absent('authorized_key')
            .result_json({
                'linux': create_linux_active(dist='Arch Linux latest minimal', lang='en'),
            })
            .expect_url('{0}/boot/23/linux'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'install_linux'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_install_linux_reactivate(self, mocker):
        result = self.run_module_success(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'install_linux': {
                'dist': 'Debian 11 base',
                'arch': 32,
                'lang': 'fr',
                'authorized_keys': [
                    'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0',
                    'aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99',
                ],
            },
        }, [
            FetchUrlCall('GET', 200)
            .result_json(_amend_boot({
                'linux': create_linux_active(dist='Arch Linux latest minimal', lang='en'),
            }))
            .expect_url('{0}/boot/23'.format(BASE_URL)),
            FetchUrlCall('DELETE', 200)
            .expect_url('{0}/boot/23/linux'.format(BASE_URL)),
            FetchUrlCall('POST', 200)
            .expect_form_value('dist', 'Debian 11 base')
            .expect_form_value('arch', '32')
            .expect_form_value('lang', 'fr')
            .expect_form_present('authorized_key')
            # .expect_form_value('authorized_key', 'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0')
            # .expect_form_value('authorized_key', 'aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99')
            .result_json({
                'linux': create_linux_active(dist='Debian 11 base', lang='fr', arch=32, authorized_key=[
                    {
                        'key': {
                            'fingerprint': 'aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99',
                            'name': 'foo bar',
                            'size': 4096,
                            'type': 'RSA',
                        },
                    },
                    {
                        'key': {
                            'fingerprint': 'e4:47:42:71:81:62:bf:06:1c:23:fa:f3:8f:7b:6f:d0',
                            'name': 'bar',
                            'size': 2048,
                            'type': 'RSA',
                        },
                    },
                ]),
            })
            .expect_url('{0}/boot/23/linux'.format(BASE_URL)),
        ])
        assert result['changed'] is True
        assert result['configuration_type'] == 'install_linux'
        assert result['password'] == 'aBcDeFgHiJ1234'

    def test_server_not_found(self, mocker):
        result = self.run_module_failed(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'regular_boot': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'SERVER_NOT_FOUND',
                    'message': 'Server not found',
                },
            })
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'This server does not exist, or you do not have access rights for it'

    def test_invalid_input(self, mocker):
        result = self.run_module_failed(mocker, boot, {
            'hetzner_user': '',
            'hetzner_password': '',
            'server_number': 23,
            'regular_boot': True,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'BOOT_NOT_AVAILABLE',
                    'message': 'No boot configuration available for this server',
                },
            })
            .expect_url('{0}/boot/23'.format(BASE_URL)),
        ])
        assert result['msg'] == 'There is no boot configuration available for this server'
