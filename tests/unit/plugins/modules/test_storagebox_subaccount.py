# Copyright (c) 2025 Victor LEFEBVRE <dev@vic1707.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.community.internal_test_tools.tests.unit.utils.fetch_url_module_framework import (
    FetchUrlCall,
    BaseTestModule,
)

from ansible_collections.community.hrobot.plugins.module_utils.robot import BASE_URL
from ansible_collections.community.hrobot.plugins.modules import (
    storagebox_subaccount,
)

STORAGEBOX_SUBACCOUNTS = [
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


class TestHetznerStorageboxSubbacount(BaseTestModule):
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
            .result_json(STORAGEBOX_SUBACCOUNTS)
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
            .result_json(STORAGEBOX_SUBACCOUNTS)
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
            .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                'username': "I'll be ignored"
            },
            [
                FetchUrlCall('GET', 200)
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount'),

                FetchUrlCall('PUT', 200)
                .expect_url(BASE_URL + '/storagebox/1234/subaccount/' + STORAGEBOX_SUBACCOUNTS[0]['subaccount']['username'])
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
                .result_json(STORAGEBOX_SUBACCOUNTS)
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
            .result_json(STORAGEBOX_SUBACCOUNTS)
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
            'comment': STORAGEBOX_SUBACCOUNTS[0]['subaccount']['comment'],
        }, [
            FetchUrlCall('GET', 200)
            .result_json([STORAGEBOX_SUBACCOUNTS[0], STORAGEBOX_SUBACCOUNTS[0]])
            .expect_url(BASE_URL + '/storagebox/1234/subaccount')
        ])

        assert result['msg'] == "More than one subaccount matched the idempotence criteria."
