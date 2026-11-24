python-androidtv
================

.. image:: https://github.com/TiDo12345/python-androidtv/actions/workflows/python-package.yml/badge.svg?branch=master
   :target: https://github.com/TiDo12345/python-androidtv/actions/workflows/python-package.yml
   :alt: Build Status

``androidtv`` is a Python package that provides state information and control of Android TV and Fire TV devices via ADB.  It is used by the `Android TV <https://www.home-assistant.io/integrations/androidtv/>`_ integration in Home Assistant.

**This is a maintained fork** of `JeffLIrion/python-androidtv <https://github.com/JeffLIrion/python-androidtv>`_ (``androidtv`` on PyPI).


About this fork
---------------

The original project only accepts community pull requests and has not had a release since 0.0.75 (November 2024).  Several fixes that are needed in practice, in particular for Fire TV / Fire OS devices controlled from Home Assistant, are waiting there as open pull requests.  This fork collects them, keeps the package working on current Python versions and is maintained for that use.

Changes compared to ``androidtv`` 0.0.75:

* Python 3.11+ only; CI runs on Python 3.11 to 3.15 (based on upstream pull requests `#361 <https://github.com/JeffLIrion/python-androidtv/pull/361>`_ and `#364 <https://github.com/JeffLIrion/python-androidtv/pull/364>`_ to `#366 <https://github.com/JeffLIrion/python-androidtv/pull/366>`_ by CloCkWeRX)
* screencap on Fire OS: strip the text line printed before the PNG data (issue `#377 <https://github.com/JeffLIrion/python-androidtv/issues/377>`_)
* longer timeout for file transfers (``push`` / ``pull``)
* queue ADB commands instead of dropping them while the connection is busy, e.g. during a screencap (async: upstream pull request `#374 <https://github.com/JeffLIrion/python-androidtv/pull/374>`_ by Komzpa; sync: same change); a command waits at most 60 s, and is not sent if the connection was closed while it waited
* discard ``dumpsys`` stderr so that "Broken pipe" does not corrupt the parsed state (upstream pull request `#376 <https://github.com/JeffLIrion/python-androidtv/pull/376>`_ by JordiRubio93, issue `#373 <https://github.com/JeffLIrion/python-androidtv/issues/373>`_)
* retry the power check up to 20 times, with a short pause, when ``dumpsys power`` fails (upstream pull request `#367 <https://github.com/JeffLIrion/python-androidtv/pull/367>`_ by matejdro)
* check whether the screen is on with ``dumpsys deviceidle get screen`` first, then the previous checks (upstream pull request `#369 <https://github.com/JeffLIrion/python-androidtv/pull/369>`_ by tgrushka; checked on a Fire OS 7 (Android 9) TV)
* device properties are no longer discarded when the manufacturer or product ID is empty (same problem as upstream pull request `#359 <https://github.com/JeffLIrion/python-androidtv/pull/359>`_ by clansty)
* no Python 2 compatibility code and no direct ``async_timeout`` dependency any more; requires ``adb-shell`` 0.4.4+
* packaging with ``pyproject.toml`` (version defined only in ``androidtv/__init__.py``); hardened CI (read-only token, GitHub Actions pinned to commit SHAs, pinned tools, weekly run), Dependabot, CodeQL and secret scanning


Installation
------------

There is no PyPI release of this fork.  The version carries a local label (currently ``0.0.75+tido.6``), so it still satisfies a requirement of ``androidtv==0.0.75``, such as the one in Home Assistant.

Install a release (recommended, a fixed version) with the wheel URL from the `releases page <https://github.com/TiDo12345/python-androidtv/releases>`_:

.. code-block::

   pip install "androidtv[async] @ https://github.com/TiDo12345/python-androidtv/releases/download/<tag>/<wheel>"

or the current ``master`` branch:

.. code-block::

   pip install "androidtv[async] @ git+https://github.com/TiDo12345/python-androidtv"

The ``async`` extra is needed for the async classes (as used by Home Assistant); leave it out for the sync classes only.


Documentation
-------------

The API documentation of the original package at `https://androidtv.readthedocs.io <https://androidtv.readthedocs.io>`_ still applies; this fork does not change the public API.  The documentation sources are in ``docs/``.


Contributing and issues
-----------------------

Please report problems with this fork in `its issue tracker <https://github.com/TiDo12345/python-androidtv/issues>`_ and report security issues privately via `GitHub security advisories <https://github.com/TiDo12345/python-androidtv/security/advisories/new>`_.  Pull requests are welcome; they need to pass all CI checks (black, flake8, pylint and the tests with full coverage of the changed code, see the ``Makefile``).


ADB Intents and Commands
------------------------

A collection of useful intents and commands can be found `here <https://gist.github.com/mcfrojd/9e6875e1db5c089b1e3ddeb7dba0f304>`_ (credit: mcfrojd).


Acknowledgments
---------------

Many thanks to Jeff Irion, who wrote and maintained this package for years, to all contributors of the original project, and to the authors of the pull requests listed above.

The original package is based on `python-firetv <https://github.com/happyleavesaoc/python-firetv>`_ by happyleavesaoc and the `androidtv component for Home Assistant <https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py>`_ by a1ex4, and it depends on the Python packages `adb-shell <https://github.com/JeffLIrion/adb_shell>`_ (which is based on `python-adb <https://github.com/google/python-adb>`_) and `pure-python-adb <https://github.com/Swind/pure-python-adb>`_.


License
-------

MIT License, as the original project (see ``LICENSE``).
