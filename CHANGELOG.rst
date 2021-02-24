================================================
Community Hetzner Robot Collection Release Notes
================================================

.. contents:: Topics


v1.1.1
======

Release Summary
---------------

Bugfix release which reduces the number of HTTPS queries for the modules and plugins.

Bugfixes
--------

- robot - force HTTP basic authentication to reduce number of HTTPS requests (https://github.com/ansible-collections/community.hrobot/pull/9).

v1.1.0
======

Release Summary
---------------

Release with a new inventory plugin.

New Plugins
-----------

Inventory
~~~~~~~~~

- robot - Hetzner Robot inventory source

v1.0.0
======

Release Summary
---------------

The ``community.hrobot`` continues the work on the Hetzner Robot modules from their state in ``community.general`` 1.2.0. The changes listed here are thus relative to the modules ``community.general.hetzner_*``.


Breaking Changes / Porting Guide
--------------------------------

- firewall - now requires the `ipaddress <https://pypi.org/project/ipaddress/>`_ library (https://github.com/ansible-collections/community.hrobot/pull/2).
