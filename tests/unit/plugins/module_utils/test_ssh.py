# Copyright (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import pytest

from ansible_collections.community.hrobot.plugins.module_utils.ssh import (
    FingerprintError,
    normalize_fingerprint,
    extract_fingerprint,
)

from ..data import (
    SSH_PUBLIC_KEY_1,
    SSH_FINGERPRINT_1,
)


def test_normalize_fingerprint():
    assert normalize_fingerprint(SSH_FINGERPRINT_1) == SSH_FINGERPRINT_1
    assert normalize_fingerprint('F5:7e:4f:d8:ab:20:b8:5B:8b:2f:7a:4:47:fd:96:73') == (
        'f5:7e:4f:d8:ab:20:b8:5b:8b:2f:7a:04:47:fd:96:73'
    )
    assert normalize_fingerprint('F57e4fd8ab20b85B8b2f7a0447fd9673') == (
        'f5:7e:4f:d8:ab:20:b8:5b:8b:2f:7a:04:47:fd:96:73'
    )
    assert normalize_fingerprint('Fe:F', size=2) == 'fe:0f'

    with pytest.raises(FingerprintError) as exc:
        normalize_fingerprint('')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Fingerprint must consist of 16 8-bit hex numbers: got 0 8-bit hex numbers instead'
    with pytest.raises(FingerprintError) as exc:
        normalize_fingerprint('1:2:3')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Fingerprint must consist of 16 8-bit hex numbers: got 3 8-bit hex numbers instead'
    with pytest.raises(FingerprintError) as exc:
        normalize_fingerprint('01023')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Fingerprint must consist of 16 8-bit hex numbers: got 3 8-bit hex numbers instead'

    with pytest.raises(FingerprintError) as exc:
        normalize_fingerprint('A:B:C:D:E:F:G:H:I:J:K:L:M:N:O:P')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Fingerprint must consist of 16 8-bit hex numbers: number 7 is invalid: "G"'
    with pytest.raises(FingerprintError) as exc:
        normalize_fingerprint('fee:B:C:D:E:F:G:H:I:J:K:L:M:N:O:P')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Fingerprint must consist of 16 8-bit hex numbers: number 1 is invalid: "fee"'


def test_extract_fingerprint():
    assert extract_fingerprint(SSH_PUBLIC_KEY_1) == SSH_FINGERPRINT_1
    assert extract_fingerprint('   %s   foo@ bar   ' % SSH_PUBLIC_KEY_1.replace(' ', '    ')) == SSH_FINGERPRINT_1

    key = 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGGdztn98LzAZkwHzSNa2HpTERPzBZdrdMt9u++0qQ+U'
    assert extract_fingerprint(key) == 'f5:7e:4f:d8:ab:20:b8:5b:8b:2f:7a:04:47:fd:96:73'
    print(extract_fingerprint(key, alg='sha256', size=32))
    assert extract_fingerprint(key, alg='sha256', size=32) == (
        '64:94:70:47:7a:bd:79:99:95:9f:3b:d3:37:8c:2c:fa:33:a7:d1:93:95:56:1b:f7:f6:52:31:34:0b:4a:fc:67'
    )

    key = (
        'ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDEVarUR'
        'tu+DmCvn0OkHC+gCOQ6Bxkolfh9NvWr4f8SPfQJ/yOUO6RZ+m3RhvnDEWAvA1BG/lCNqui6/kuZiyVk='
    )
    assert extract_fingerprint(key) == 'f4:b7:43:14:fe:8b:43:4b:cc:b3:63:dc:cf:23:bb:cb'
    print(extract_fingerprint(key, alg='sha256', size=32))
    assert extract_fingerprint(key, alg='sha256', size=32) == (
        '88:c2:a3:0f:2a:cf:60:73:7c:52:e0:41:40:25:c3:d4:5d:32:37:a9:46:48:3e:37:34:f1:aa:0d:4d:69:15:d7'
    )

    with pytest.raises(FingerprintError) as exc:
        extract_fingerprint('  adsf  ')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Error while extracting fingerprint from public key data: cannot split public key into at least two parts'

    with pytest.raises(FingerprintError) as exc:
        extract_fingerprint('a b')
    print(exc.value.args[0])
    assert exc.value.args[0] in (
        'Error while extracting fingerprint from public key data: Invalid base64-encoded string:'
        ' number of data characters (1) cannot be 1 more than a multiple of 4',
        'Error while extracting fingerprint from public key data: Incorrect padding',
    )
    with pytest.raises(FingerprintError) as exc:
        extract_fingerprint('a ab=f')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Error while extracting fingerprint from public key data: Incorrect padding'
    with pytest.raises(FingerprintError) as exc:
        extract_fingerprint('a ab==', alg='foo bar')
    print(exc.value.args[0])
    assert exc.value.args[0] == 'Hash algorithm FOO BAR is not available. Possibly running in FIPS mode.'
