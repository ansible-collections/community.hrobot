# Copyright (c) 2025 Victor LEFEBVRE <dev@vic1707.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import MagicMock

from ansible_collections.community.hrobot.plugins.module_utils.api import API_BASE_URL
from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import (
    storagebox_subaccount,
)

LEGACY_STORAGEBOX_SUBACCOUNTS = [
    {
        "subaccount": {
            "username": "u2342-sub1",
            "accountid": "u2342",
            "server": "u12345-sub1.your-storagebox.de",
            "homedirectory": "test",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": False,
            "readonly": False,
            "createtime": "2017-05-24 00:00:00",
            "comment": "Test account",
        }
    },
    {
        "subaccount": {
            "username": "u2342-sub2",
            "accountid": "u2342",
            "server": "u12345-sub2.your-storagebox.de",
            "homedirectory": "test2",
            "samba": False,
            "ssh": True,
            "external_reachability": True,
            "webdav": True,
            "readonly": False,
            "createtime": "2025-01-24 00:00:00",
            "comment": "Test account 2",
        }
    },
]


STORAGEBOX_SUBACCOUNTS = [
    {
        "id": 1,
        "username": "u2342-sub1",
        "server": "u12345-sub1.your-storagebox.de",
        "storage_box": 2342,
        "home_directory": "test",
        "access_settings": {
            "samba_enabled": True,
            "ssh_enabled": True,
            "webdav_enabled": False,
            "reachable_externally": True,
            "readonly": False,
        },
        "description": "Test account",
        "created": "2017-05-24 00:00:00",
        "labels": {},
    },
    {
        "id": 2,
        "username": "u2342-sub2",
        "server": "u12345-sub2.your-storagebox.de",
        "storage_box": 2342,
        "home_directory": "test2",
        "access_settings": {
            "samba_enabled": False,
            "ssh_enabled": True,
            "webdav_enabled": True,
            "reachable_externally": True,
            "readonly": False,
        },
        "description": "Test account 2",
        "created": "2025-01-24 00:00:00",
        "labels": {},
    },
]


class TestHetznerStorageboxSubbacountLegacy(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_subaccount.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.robot.fetch_url'

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'status': 404,
                    'code': 'STORAGEBOX_NOT_FOUND',
                    'message': 'Storage Box with ID 23 does not exist',
                }
            })
            .expect_url(BASE_URL + '/storagebox/23/subaccount')
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'

    def test_delete_unknown_subaccount_noop(self, mocker):
        """Test deletion of a subaccount that doesn't exist (no-op)."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'username': 'ghost_user',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
            .expect_url(BASE_URL + '/storagebox/1234/subaccount')
        ])

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_delete_existing_subaccount(self, mocker):
        """Test successful deletion of an existing subaccount."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'username': 'u2342-sub2',
        }, [
            FetchUrlCall('GET', 200)
            .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
            .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

            FetchUrlCall('DELETE', 200)
            .result_json({})
            .expect_url(BASE_URL + '/storagebox/1234/subaccount/u2342-sub2')
        ])

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is True
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_delete_existing_subaccount_idempotence_by_comment(self, mocker):
        """Test successful deletion of an existing subaccount."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'comment': 'Test account',
            'idempotence': 'comment'
        }, [
            FetchUrlCall('GET', 200)
            .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
            .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

            FetchUrlCall('DELETE', 200)
            .result_json({})
            .expect_url(BASE_URL + '/storagebox/1234/subaccount/u2342-sub1')
        ])

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is True
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_create_subaccount(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount'
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
                .expect_form_value('homedirectory', '/data/newsub')
                .expect_form_value('samba', 'true')
                .expect_form_value('ssh', 'false')
                .expect_form_value('webdav', 'true')
                .expect_form_value('readonly', 'false')
                .expect_form_value('comment', 'My new subaccount')
                .result_json({
                    'subaccount': {
                        'username': 'generated_user',
                        'homedirectory': '/data/newsub',
                        'password': 'autogeneratedpass123'
                    }
                }),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'generated_user',
            'homedirectory': '/data/newsub',
            'password': 'autogeneratedpass123',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount',
        }

    # Ensures providing a username doesn't trigger accidental update (if username isn't known)
    def test_create_subaccount_unknown_username(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount data
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount',
                'username': "I'll be ignored",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
                .expect_form_value('homedirectory', '/data/newsub')
                .expect_form_value('samba', 'true')
                .expect_form_value('ssh', 'false')
                .expect_form_value('webdav', 'true')
                .expect_form_value('readonly', 'false')
                .expect_form_value('comment', 'My new subaccount')
                .result_json({
                    'subaccount': {
                        'username': 'generated_user',
                        'homedirectory': '/data/newsub',
                        'password': 'autogeneratedpass123'
                    }
                }),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'generated_user',
            'homedirectory': '/data/newsub',
            'password': 'autogeneratedpass123',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount',
        }

    def test_create_subaccount_set_to_random(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'password_mode': 'set-to-random',
                # subaccount
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount',
                'password': 'toto'
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
                .expect_form_value('homedirectory', '/data/newsub')
                .expect_form_value('samba', 'true')
                .expect_form_value('ssh', 'false')
                .expect_form_value('webdav', 'true')
                .expect_form_value('readonly', 'false')
                .expect_form_value('comment', 'My new subaccount')
                .expect_form_value_absent('password')
                .result_json({
                    'subaccount': {
                        'username': 'generated_user',
                        'homedirectory': '/data/newsub',
                        'password': 'autogeneratedpass123'
                    }
                }),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'generated_user',
            'homedirectory': '/data/newsub',
            'password': 'autogeneratedpass123',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount',
        }

    def test_create_subaccount_limit_exceeded(self, mocker):
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount'
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 400)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
                .expect_form_value('homedirectory', '/data/newsub')
                .expect_form_value('samba', 'true')
                .expect_form_value('ssh', 'false')
                .expect_form_value('webdav', 'true')
                .expect_form_value('readonly', 'false')
                .expect_form_value('comment', 'My new subaccount')
                .result_json({
                    "error": {
                        "status": 400,
                        "code": "STORAGEBOX_SUBACCOUNT_LIMIT_EXCEEDED",
                        "message": "Too many requests"
                    }
                })
            ]
        )
        assert result['msg'] == "Subaccount limit exceeded"

    def test_create_subaccount_invalid_password(self, mocker):
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'Invalid password attempt',
                'password': '123'
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 400)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
                .expect_form_value("password", "123")
                .result_json({
                    "error": {
                        "status": 400,
                        "code": "STORAGEBOX_INVALID_PASSWORD",
                        "message": "Password does not meet security requirements"
                    }
                })
            ]
        )

        assert result['msg'] == "Invalid password (says Hetzner)"

    def test_update_subaccount_noop(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),
            ]
        )

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
        }

    def test_update_subaccount_noop_idempotence_by_comment(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount
                'idempotence': 'comment',
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),
            ]
        )

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
        }

    def test_update_subaccount(self, mocker):
        input = {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            # subaccount
            "username": "u2342-sub1",
            "homedirectory": "test",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": False,
            "readonly": False,
            "comment": "new comment",
        }
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            input,
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('PUT', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/' + input['username'])
                .expect_form_value("homedirectory", input["homedirectory"])
                .expect_form_value("samba", str(input["samba"]).lower())
                .expect_form_value("ssh", str(input["ssh"]).lower())
                .expect_form_value("external_reachability", str(input["external_reachability"]).lower())
                .expect_form_value("webdav", str(input["webdav"]).lower())
                .expect_form_value("readonly", str(input["readonly"]).lower())
                .expect_form_value("comment", input["comment"])
                .result_json({})
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'new comment',
        }

    def test_update_subaccount_idempotence_by_comment(self, mocker):
        input = {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            # subaccount
            'idempotence': 'comment',
            "homedirectory": "/new/homedir",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": False,
            "readonly": False,
            "comment": "Test account",
        }
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            input,
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('PUT', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/' + LEGACY_STORAGEBOX_SUBACCOUNTS[0]['subaccount']['username'])
                .expect_form_value("homedirectory", input["homedirectory"])
                .expect_form_value("samba", str(input["samba"]).lower())
                .expect_form_value("ssh", str(input["ssh"]).lower())
                .expect_form_value("external_reachability", str(input["external_reachability"]).lower())
                .expect_form_value("webdav", str(input["webdav"]).lower())
                .expect_form_value("readonly", str(input["readonly"]).lower())
                .expect_form_value("comment", input["comment"])
                .result_json({})
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': '/new/homedir',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
        }

    def test_update_subaccount_set_to_random(self, mocker):
        input = {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            # subaccount
            "username": "u2342-sub1",
            "homedirectory": "test",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": False,
            "readonly": False,
            "comment": "new comment",
            "password": "toto",
            "password_mode": "set-to-random",
        }
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            input,
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/' + input['username'] + '/password')
                .expect_form_value_absent("password")
                .result_json({"password": "newRandomPassword"}),

                FetchUrlCall('PUT', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/' + input['username'])
                .expect_form_value("homedirectory", input["homedirectory"])
                .expect_form_value("samba", str(input["samba"]).lower())
                .expect_form_value("ssh", str(input["ssh"]).lower())
                .expect_form_value("external_reachability", str(input["external_reachability"]).lower())
                .expect_form_value("webdav", str(input["webdav"]).lower())
                .expect_form_value("readonly", str(input["readonly"]).lower())
                .expect_form_value("comment", input["comment"])
                .result_json({})
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is True
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'new comment',
            'password': 'newRandomPassword',
        }

    def test_update_password_only(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # account
                "password": "newsecurepassword",
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/u2342-sub1/password')
                .expect_form_value("password", "newsecurepassword")
                .result_json({"password": "newsecurepassword"})
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is True
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
            'password': 'newsecurepassword',
        }

    def test_update_subaccount_invalid_password(self, mocker):
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount
                "password": "123",
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('POST', 400)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/u2342-sub1/password')
                .expect_form_value("password", "123")
                .result_json({
                    "error": {
                        "status": 400,
                        "code": "STORAGEBOX_INVALID_PASSWORD",
                        "message": "Password does not meet security requirements"
                    }
                })
            ]
        )

        assert result['msg'] == "Invalid password (says Hetzner)"

    def test_invalid_spec_create_no_homedir(self, mocker):
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                'state': 'present',
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
            ]
        )

        assert result['msg'] == "homedirectory is required when creating a new subaccount"

    # Check mode tests
    def test_update_password_only_CHECK_MODE(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                '_ansible_check_mode': True,
                # subaccount
                "password": "newsecurepassword",
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is True
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
            'password': 'newsecurepassword',
        }

    def test_create_subaccount_CHECK_MODE(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                # subaccount,
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount',
                '_ansible_check_mode': True,
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'homedirectory': '/data/newsub',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount',
        }

    def test_update_subaccount_CHECK_MODE(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_user': '',
                'hetzner_password': '',
                'storagebox_id': 1234,
                '_ansible_check_mode': True,
                # subaccount
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "new comment",

            },
            [
                FetchUrlCall('GET', 200)
                .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount')
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'username': 'u2342-sub1',
            'accountid': 'u2342',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'createtime': '2017-05-24 00:00:00',
            'comment': 'new comment',
        }

    def test_delete_existing_subaccount_CHECK_MODE(self, mocker):
        """Test successful deletion of an existing subaccount."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'username': 'u2342-sub2',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json(LEGACY_STORAGEBOX_SUBACCOUNTS)
            .expect_url(BASE_URL + '/storagebox/1234/subaccount')
        ])

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is True
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_broken_idempotence_same_comment_multiple_accounts(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_user': '',
            'hetzner_password': '',
            'storagebox_id': 1234,
            'idempotence': 'comment',
            'comment': LEGACY_STORAGEBOX_SUBACCOUNTS[0]['subaccount']['comment'],
        }, [
            FetchUrlCall('GET', 200)
            .result_json([LEGACY_STORAGEBOX_SUBACCOUNTS[0], LEGACY_STORAGEBOX_SUBACCOUNTS[0]])
            .expect_url(BASE_URL + '/storagebox/1234/subaccount')
        ])

        assert result['msg'] == "More than one subaccount matched the idempotence criteria."


class TestHetznerStorageboxSubbacount(BaseTestModule):
    MOCK_ANSIBLE_MODULEUTILS_BASIC_ANSIBLEMODULE = 'ansible_collections.community.hrobot.plugins.modules.storagebox_subaccount.AnsibleModule'
    MOCK_ANSIBLE_MODULEUTILS_URLS_FETCH_URL = 'ansible_collections.community.hrobot.plugins.module_utils.api.fetch_url'

    def test_storagebox_id_unknown(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 23,
        }, [
            FetchUrlCall('GET', 404)
            .result_json({
                'error': {
                    'code': 'not_found',
                    'message': 'Storage Box not found',
                    'details': {},
                }
            })
            .expect_url('{0}/v1/storage_boxes/23/subaccounts'.format(API_BASE_URL))
        ])
        assert result['msg'] == 'Storagebox with ID 23 does not exist'

    def test_delete_unknown_subaccount_noop(self, mocker):
        """Test deletion of a subaccount that doesn't exist (no-op)."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'username': 'ghost_user',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "subaccounts": STORAGEBOX_SUBACCOUNTS,
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
        ])

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_delete_existing_subaccount(self, mocker):
        """Test successful deletion of an existing subaccount."""
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'username': 'u2342-sub2',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "subaccounts": STORAGEBOX_SUBACCOUNTS,
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

            FetchUrlCall('DELETE', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_subaccount",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_subaccount"
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts/2'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_subaccount",
                    "status": "success",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 1234,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_subaccount"
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is True
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_delete_existing_subaccount_idempotence_by_comment(self, mocker):
        """Test successful deletion of an existing subaccount."""
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'comment': 'Test account',
            'idempotence': 'comment'
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "subaccounts": STORAGEBOX_SUBACCOUNTS,
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

            FetchUrlCall('DELETE', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_subaccount",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 1234,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_subaccount"
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_subaccount",
                    "status": "success",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_subaccount"
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
        ])

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is True
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_delete_existing_subaccount_fail(self, mocker):
        """Test successful deletion of an existing subaccount."""
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'username': 'u2342-sub2',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "subaccounts": STORAGEBOX_SUBACCOUNTS,
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

            FetchUrlCall('DELETE', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_subaccount",
                    "status": "running",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": None,
                    "resources": [
                        {
                            "id": 23,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_subaccount"
                        },
                    ],
                    "error": None,
                }
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts/2'.format(API_BASE_URL)),
            FetchUrlCall('GET', 200)
            .result_json({
                "action": {
                    "id": 13,
                    "command": "delete_subaccount",
                    "status": "error",
                    "progress": 0,
                    "started": "2016-01-30T23:50:00+00:00",
                    "finished": "2016-01-30T23:50:00+00:00",
                    "resources": [
                        {
                            "id": 1234,
                            "type": "storage_box",
                        },
                        {
                            "id": 1,
                            "type": "storage_box_subaccount"
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

        assert result['msg'] == "Error while deleting subaccount: [action_failed] Action failed"

    def test_create_subaccount(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount',
                'password': 'toto',
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
                .expect_json_value(['home_directory'], 'data/newsub')
                .expect_json_value(['access_settings', 'samba_enabled'], True)
                .expect_json_value(['access_settings', 'ssh_enabled'], False)
                .expect_json_value(['access_settings', 'webdav_enabled'], True)
                .expect_json_value(['access_settings', 'readonly'], False)
                .expect_json_value(['description'], 'My new subaccount')
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "create_subaccount",
                        "status": "running",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": None,
                        "resources": [
                            {
                                "id": 23,
                                "type": "storage_box",
                            },
                            {
                                "id": 1,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                }),
                FetchUrlCall('GET', 200)
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "create_subaccount",
                        "status": "success",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": "2016-01-30T23:50:00+00:00",
                        "resources": [
                            {
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 1,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    }
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccount": STORAGEBOX_SUBACCOUNTS[0],
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1'.format(API_BASE_URL)),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'readonly': False,
                'reachable_externally': True,
                'samba_enabled': True,
                'ssh_enabled': False,
                'webdav_enabled': True,
            },
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'comment': 'My new subaccount',
            'description': 'My new subaccount',
            'external_reachability': True,
            'home_directory': '/data/newsub',
            'homedirectory': '/data/newsub',
            'id': 1,
            'labels': {},
            'password': 'toto',
            'readonly': False,
            'samba': True,
            'server': 'u12345-sub1.your-storagebox.de',
            'ssh': False,
            'storage_box': 2342,
            'username': 'u2342-sub1',
            'webdav': True,
        }

    # Ensures providing a username doesn't trigger accidental update (if username isn't known)
    def test_create_subaccount_unknown_username(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount data
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount',
                'username': "I'll be ignored",
                'password': 'toto',
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
                .expect_json_value(['home_directory'], 'data/newsub')
                .expect_json_value(['access_settings', 'samba_enabled'], True)
                .expect_json_value(['access_settings', 'ssh_enabled'], False)
                .expect_json_value(['access_settings', 'webdav_enabled'], True)
                .expect_json_value(['access_settings', 'readonly'], False)
                .expect_json_value(['description'], 'My new subaccount')
                .expect_json_value(['password'], 'toto')
                .expect_json_value_absent(['username'])
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "create_subaccount",
                        "status": "running",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": None,
                        "resources": [
                            {
                                "id": 23,
                                "type": "storage_box",
                            },
                            {
                                "id": 2,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                }),
                FetchUrlCall('GET', 200)
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "create_subaccount",
                        "status": "success",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": "2016-01-30T23:50:00+00:00",
                        "resources": [
                            {
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 2,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    }
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccount": STORAGEBOX_SUBACCOUNTS[1],
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/2'.format(API_BASE_URL)),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': True,
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': False,
                'webdav_enabled': True,
            },
            'comment': 'My new subaccount',
            'created': '2025-01-24 00:00:00',
            'createtime': '2025-01-24 00:00:00',
            'description': 'My new subaccount',
            'external_reachability': True,
            'home_directory': '/data/newsub',
            'homedirectory': '/data/newsub',
            'id': 2,
            'labels': {},
            'password': 'toto',
            'readonly': False,
            'samba': True,
            'server': 'u12345-sub2.your-storagebox.de',
            'ssh': False,
            'storage_box': 2342,
            'username': 'u2342-sub2',
            'webdav': True,
        }

    def test_create_subaccount_set_to_random(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            'password_mode': 'set-to-random',
            # subaccount
            'homedirectory': '/data/newsub',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount',
            'password': 'toto'
        }, [])

        assert result['msg'] == 'The new Hetzner API does not support password_mode=set-to-random'

    def test_create_subaccount_no_password(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            # subaccount
            'homedirectory': '/data/newsub',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount',
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "subaccounts": STORAGEBOX_SUBACCOUNTS,
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),
        ])

        assert result['msg'] == 'password is required when creating a new subaccount'

    def test_create_subaccount_limit_exceeded(self, mocker):
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount',
                'password': 'toto',
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 400)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
                .expect_json_value(['home_directory'], 'data/newsub')
                .expect_json_value(['access_settings', 'samba_enabled'], True)
                .expect_json_value(['access_settings', 'ssh_enabled'], False)
                .expect_json_value(['access_settings', 'webdav_enabled'], True)
                .expect_json_value(['access_settings', 'readonly'], False)
                .expect_json_value(['description'], 'My new subaccount')
                .expect_json_value(['password'], 'toto')
                .expect_json_value_absent(['username'])
                .result_json({
                    "error": {
                        "code": "resource_limit_exceeded",
                        "message": "snapshot limit exceeded",
                        "details": {
                            "limits": [
                                {
                                    "name": "subaccount_limit"
                                },
                            ],
                        },
                    },
                }),
            ]
        )
        assert result['msg'] in (
            "Request failed: [resource_limit_exceeded] snapshot limit exceeded. Details: {'limits': [{'name': 'subaccount_limit'}]}",
            "Request failed: [resource_limit_exceeded] snapshot limit exceeded. Details: {u'limits': [{u'name': u'subaccount_limit'}]}",
        )

    def test_create_subaccount_invalid_password(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'Invalid password attempt',
                'password': '123',
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
                .expect_json_value(['home_directory'], 'data/newsub')
                .expect_json_value(['access_settings', 'samba_enabled'], True)
                .expect_json_value(['access_settings', 'ssh_enabled'], False)
                .expect_json_value(['access_settings', 'webdav_enabled'], True)
                .expect_json_value(['access_settings', 'readonly'], False)
                .expect_json_value(['description'], 'Invalid password attempt')
                .expect_json_value(['password'], '123')
                .expect_json_value_absent(['username'])
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "create_subaccount",
                        "status": "running",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": None,
                        "resources": [
                            {
                                "id": 23,
                                "type": "storage_box",
                            },
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                }),
                FetchUrlCall('GET', 200)
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "create_subaccount",
                        "status": "error",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": "2016-01-30T23:50:00+00:00",
                        "resources": [
                            {
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": {
                            "code": "action_failed",
                            "message": "Action failed",
                        },
                    },
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            ]
        )

        assert result['msg'] == "Error while creating subaccount: [action_failed] Action failed"

    def test_update_subaccount_noop(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),
            ]
        )

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': True,
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': True,
                'webdav_enabled': False,
            },
            'username': 'u2342-sub1',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'home_directory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
            'description': 'Test account',
            'id': 1,
            'labels': {},
            'storage_box': 2342,
        }

    def test_update_subaccount_noop_idempotence_by_comment(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount
                'idempotence': 'comment',
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),
            ]
        )

        assert result['changed'] is False
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': True,
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': True,
                'webdav_enabled': False,
            },
            'username': 'u2342-sub1',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'home_directory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
            'description': 'Test account',
            'id': 1,
            'labels': {},
            'storage_box': 2342,
        }

    def test_update_subaccount(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        input = {
            'hetzner_token': '',
            'storagebox_id': 1234,
            # subaccount
            "username": "u2342-sub1",
            "homedirectory": "test",
            "samba": True,
            "ssh": True,
            "external_reachability": False,
            "webdav": True,
            "readonly": False,
            "comment": "new comment",
        }
        updated_1 = dict(STORAGEBOX_SUBACCOUNTS[0])
        updated_1['home_directory'] = '/test'
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            input,
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('PUT', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1'.format(API_BASE_URL))
                .expect_json_value(["description"], 'new comment')
                .result_json({
                    "subaccount": updated_1,
                }),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1/actions/update_access_settings'.format(API_BASE_URL))
                .expect_json_value_absent(["home_directory"])
                .expect_json_value_absent(["samba_enabled"])
                .expect_json_value_absent(["ssh_enabled"])
                .expect_json_value(["reachable_externally"], False)
                .expect_json_value(["webdav_enabled"], True)
                .expect_json_value_absent(["readonly"])
                .expect_json_value_absent(["description"])
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
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                }),
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
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': False,
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': True,
                'webdav_enabled': True,
            },
            'comment': 'new comment',
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'description': 'new comment',
            'external_reachability': False,
            'home_directory': 'test',
            'homedirectory': 'test',
            'id': 1,
            'labels': {},
            'readonly': False,
            'samba': True,
            'server': 'u12345-sub1.your-storagebox.de',
            'ssh': True,
            'storage_box': 2342,
            'username': 'u2342-sub1',
            'webdav': True,
        }

    def test_update_subaccount_idempotence_by_comment(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        input = {
            'hetzner_token': '',
            'storagebox_id': 1234,
            # subaccount
            'idempotence': 'comment',
            "homedirectory": "/new/homedir",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": True,
            "readonly": False,
            "comment": "Test account",
        }
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            input,
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1/actions/update_access_settings'.format(API_BASE_URL))
                .expect_json_value(["home_directory"], 'new/homedir')
                .expect_json_value_absent(["samba_enabled"])
                .expect_json_value_absent(["ssh_enabled"])
                .expect_json_value_absent(["reachable_externally"])
                .expect_json_value(["webdav_enabled"], True)
                .expect_json_value_absent(["readonly"])
                .expect_json_value_absent(["comment"])
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
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                }),
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
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': True,
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': True,
                'webdav_enabled': True,
            },
            'comment': 'Test account',
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'description': 'Test account',
            'external_reachability': True,
            'home_directory': '/new/homedir',
            'homedirectory': '/new/homedir',
            'id': 1,
            'labels': {},
            'readonly': False,
            'samba': True,
            'server': 'u12345-sub1.your-storagebox.de',
            'ssh': True,
            'storage_box': 2342,
            'username': 'u2342-sub1',
            'webdav': True,
        }

    def test_update_subaccount_idempotence_by_comment_fail(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        input = {
            'hetzner_token': '',
            'storagebox_id': 1234,
            # subaccount
            'idempotence': 'comment',
            "homedirectory": "/new/homedir",
            "samba": True,
            "ssh": True,
            "external_reachability": True,
            "webdav": True,
            "readonly": False,
            "comment": "Test account",
        }
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            input,
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1/actions/update_access_settings'.format(API_BASE_URL))
                .expect_json_value(["home_directory"], 'new/homedir')
                .expect_json_value_absent(["samba_enabled"])
                .expect_json_value_absent(["ssh_enabled"])
                .expect_json_value_absent(["reachable_externally"])
                .expect_json_value(["webdav_enabled"], True)
                .expect_json_value_absent(["readonly"])
                .expect_json_value_absent(["comment"])
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
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    },
                }),
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
                            {
                                "id": 42,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": {
                            "code": "action_failed",
                            "message": "Action failed",
                        },
                    },
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            ]
        )

        assert result['msg'] == "Error while updating access settings: [action_failed] Action failed"

    def test_update_password_only(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # account
                "password": "newsecurepassword",
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1/actions/reset_subaccount_password'.format(API_BASE_URL))
                .expect_json_value(["password"], "newsecurepassword")
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "reset_subaccount_password",
                        "status": "running",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": None,
                        "resources": [
                            {
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 1,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    }
                }),
                FetchUrlCall('GET', 200)
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "reset_subaccount_password",
                        "status": "success",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": "2016-01-30T23:50:00+00:00",
                        "resources": [
                            {
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 1,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    }
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is True
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': True,
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': True,
                'webdav_enabled': False,
            },
            'username': 'u2342-sub1',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'home_directory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
            'description': 'Test account',
            'password': 'newsecurepassword',
            'id': 1,
            'labels': {},
            'storage_box': 2342,
        }

    def test_update_password_only_fail(self, mocker):
        sleep_mock = MagicMock()
        mocker.patch('time.sleep', sleep_mock)
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # account
                "password": "newsecurepassword",
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 200)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1/actions/reset_subaccount_password'.format(API_BASE_URL))
                .expect_json_value(["password"], "newsecurepassword")
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "reset_subaccount_password",
                        "status": "running",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": None,
                        "resources": [
                            {
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 1,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": None,
                    }
                }),
                FetchUrlCall('GET', 200)
                .result_json({
                    "action": {
                        "id": 13,
                        "command": "reset_subaccount_password",
                        "status": "error",
                        "progress": 0,
                        "started": "2016-01-30T23:50:00+00:00",
                        "finished": "2016-01-30T23:50:00+00:00",
                        "resources": [
                            {
                                "id": 1234,
                                "type": "storage_box",
                            },
                            {
                                "id": 1,
                                "type": "storage_box_subaccount"
                            },
                        ],
                        "error": {
                            "code": "action_failed",
                            "message": "Action failed",
                        },
                    },
                })
                .expect_url('{0}/v1/storage_boxes/actions/13'.format(API_BASE_URL)),
            ]
        )

        assert result['msg'] == "Error while updating password: [action_failed] Action failed"

    def test_update_subaccount_invalid_password(self, mocker):
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount
                "password": "123",
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL)),

                FetchUrlCall('POST', 400)
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts/1/actions/reset_subaccount_password'.format(API_BASE_URL))
                .expect_json_value(["password"], "123")
                .result_json({
                    "error": {
                        'code': 'invalid_input',
                        'message': "invalid input in field 'password': is too weak",
                        'details': {
                            'fields': [
                                {
                                    'name': 'password',
                                    'message': 'is too weak',
                                },
                            ],
                        },
                    }
                })
            ]
        )

        assert result['msg'] in (
            "Request failed: [invalid_input] invalid input in field 'password': is too weak."
            " Details: {'fields': [{'name': 'password', 'message': 'is too weak'}]}",
            # Python 3.5:
            "Request failed: [invalid_input] invalid input in field 'password': is too weak."
            " Details: {'fields': [{'message': 'is too weak', 'name': 'password'}]}",
            # Python 2.7:
            "Request failed: [invalid_input] invalid input in field 'password': is too weak."
            " Details: {u'fields': [{u'name': u'password', u'message': u'is too weak'}]}",
            "Request failed: [invalid_input] invalid input in field 'password': is too weak."
            " Details: {u'fields': [{u'message': u'is too weak', u'name': u'password'}]}",
        )

    def test_invalid_spec_create_no_homedir(self, mocker):
        result = self.run_module_failed(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                'state': 'present',
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
            ]
        )

        assert result['msg'] == "homedirectory is required when creating a new subaccount"

    # Check mode tests
    def test_update_password_only_CHECK_MODE(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                '_ansible_check_mode': True,
                # subaccount
                "password": "newsecurepassword",
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": False,
                "comment": "Test account",
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is True
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': True,
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': True,
                'webdav_enabled': False,
            },
            'username': 'u2342-sub1',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'home_directory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': False,
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'comment': 'Test account',
            'description': 'Test account',
            'id': 1,
            'labels': {},
            'storage_box': 2342,
            'password': 'newsecurepassword',
        }

    def test_create_subaccount_CHECK_MODE(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount,
                'homedirectory': '/data/newsub',
                'samba': True,
                'ssh': False,
                'webdav': True,
                'readonly': False,
                'comment': 'My new subaccount',
                'password': 'toto',
                '_ansible_check_mode': True,
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'readonly': False,
                'samba_enabled': True,
                'ssh_enabled': False,
                'webdav_enabled': True,
            },
            'description': 'My new subaccount',
            'home_directory': '/data/newsub',
            'homedirectory': '/data/newsub',
            'samba': True,
            'ssh': False,
            'webdav': True,
            'readonly': False,
            'comment': 'My new subaccount',
            'password': 'toto',
        }

    def test_create_subaccount_CHECK_MODE_less_info(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                # subaccount,
                'homedirectory': '/data/newsub',
                'comment': 'My new subaccount',
                'password': 'toto',
                '_ansible_check_mode': True,
            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
            ]
        )

        assert result['changed'] is True
        assert result['created'] is True
        assert result['deleted'] is False
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'description': 'My new subaccount',
            'home_directory': '/data/newsub',
            'homedirectory': '/data/newsub',
            'comment': 'My new subaccount',
            'password': 'toto',
        }

    def test_update_subaccount_CHECK_MODE(self, mocker):
        result = self.run_module_success(
            mocker,
            storagebox_subaccount,
            {
                'hetzner_token': '',
                'storagebox_id': 1234,
                '_ansible_check_mode': True,
                # subaccount
                "username": "u2342-sub1",
                "homedirectory": "test",
                "samba": True,
                "ssh": True,
                "external_reachability": True,
                "webdav": False,
                "readonly": True,
                "comment": "new comment",

            },
            [
                FetchUrlCall('GET', 200)
                .result_json({
                    "subaccounts": STORAGEBOX_SUBACCOUNTS,
                })
                .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
            ]
        )

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is False
        assert result['updated'] is True
        assert result['password_updated'] is False
        assert result['subaccount'] == {
            'access_settings': {
                'reachable_externally': True,
                'readonly': True,
                'samba_enabled': True,
                'ssh_enabled': True,
                'webdav_enabled': False,
            },
            'username': 'u2342-sub1',
            'server': 'u12345-sub1.your-storagebox.de',
            'homedirectory': 'test',
            'home_directory': 'test',
            'samba': True,
            'ssh': True,
            'external_reachability': True,
            'webdav': False,
            'readonly': True,
            'created': '2017-05-24 00:00:00',
            'createtime': '2017-05-24 00:00:00',
            'comment': 'new comment',
            'description': 'new comment',
            'id': 1,
            'labels': {},
            'storage_box': 2342,
        }

    def test_delete_existing_subaccount_CHECK_MODE(self, mocker):
        """Test successful deletion of an existing subaccount."""
        result = self.run_module_success(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            'state': 'absent',
            'username': 'u2342-sub2',
            '_ansible_check_mode': True,
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "subaccounts": STORAGEBOX_SUBACCOUNTS,
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
        ])

        assert result['changed'] is True
        assert result['created'] is False
        assert result['deleted'] is True
        assert result['updated'] is False
        assert result['password_updated'] is False
        assert result['subaccount'] is None

    def test_broken_idempotence_same_comment_multiple_accounts(self, mocker):
        result = self.run_module_failed(mocker, storagebox_subaccount, {
            'hetzner_token': '',
            'storagebox_id': 1234,
            'idempotence': 'comment',
            'comment': STORAGEBOX_SUBACCOUNTS[0]['description'],
        }, [
            FetchUrlCall('GET', 200)
            .result_json({
                "subaccounts": [STORAGEBOX_SUBACCOUNTS[0], STORAGEBOX_SUBACCOUNTS[0]],
            })
            .expect_url('{0}/v1/storage_boxes/1234/subaccounts'.format(API_BASE_URL))
        ])

        assert result['msg'] == "More than one subaccount matched the idempotence criteria."
