# Copyright (c) 2025 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from .utils import extract_warnings_texts


def test_extract_warnings_texts_1():
    assert extract_warnings_texts({}) == []
    assert extract_warnings_texts({'warnings': None}) == []
    assert extract_warnings_texts({'warnings': []}) == []
    assert extract_warnings_texts({'warnings': ['foo']}) == ['foo']
