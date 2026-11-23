python-androidtv
================

.. note::

   **This is a maintained fork** of `JeffLIrion/python-androidtv <https://github.com/JeffLIrion/python-androidtv>`_. The original project only accepts community pull requests and has not had a release since 0.0.75, so fixes that are needed in practice (Fire TV / Fire OS devices controlled from Home Assistant) are collected here.

   Changes compared to ``androidtv`` 0.0.75:

   * Python 3.11+ only; CI runs on Python 3.11 to 3.14 (based on upstream pull requests `#361 <https://github.com/JeffLIrion/python-androidtv/pull/361>`_ and `#364 <https://github.com/JeffLIrion/python-androidtv/pull/364>`_ to `#366 <https://github.com/JeffLIrion/python-androidtv/pull/366>`_ by CloCkWeRX)
   * screencap on Fire OS: strip the text line printed before the PNG data (issue `#377 <https://github.com/JeffLIrion/python-androidtv/issues/377>`_)
   * longer timeout for file transfers (``push`` / ``pull``)
   * queue async ADB commands instead of dropping them while the connection is busy (upstream pull request `#374 <https://github.com/JeffLIrion/python-androidtv/pull/374>`_ by Komzpa)
   * discard ``dumpsys`` stderr so that "Broken pipe" does not corrupt the parsed state (upstream pull request `#376 <https://github.com/JeffLIrion/python-androidtv/pull/376>`_ by JordiRubio93, issue `#373 <https://github.com/JeffLIrion/python-androidtv/issues/373>`_)

   There is no PyPI release of this fork. Its version carries a local label (``0.0.75+tido.1``), so it still satisfies a requirement of ``androidtv==0.0.75``. Install it from GitHub with ``pip install "androidtv[async] @ git+https://github.com/TiDo12345/python-androidtv"`` and report problems with these changes in `this repository <https://github.com/TiDo12345/python-androidtv/issues>`_.

   Many thanks to Jeff Irion and all contributors for this package, and to the authors of the pull requests above. The code remains under the original MIT License (see ``LICENSE``). The sections below are from the original README.

.. image:: https://github.com/TiDo12345/python-androidtv/actions/workflows/python-package.yml/badge.svg?branch=master
   :target: https://github.com/TiDo12345/python-androidtv/actions/workflows/python-package.yml
   :alt: Build Status
.. image:: https://coveralls.io/repos/github/JeffLIrion/python-androidtv/badge.svg
   :target: https://coveralls.io/github/JeffLIrion/python-androidtv
   :alt: Coverage Status
.. image:: https://pepy.tech/badge/androidtv
   :target: https://pepy.tech/project/androidtv
   :alt: Downloads


Contributions Only
------------------

I no longer have the time to actively work on this project, and so all future development will be from pull requests submitted by the community.  What I will do is:

* review pull requests that pass all of the CI checks
* publish new releases upon request


About
-----

Documentation for this package can be found at `https://androidtv.readthedocs.io <https://androidtv.readthedocs.io>`_.

``androidtv`` is a Python package that provides state information and control of Android TV and Fire TV devices via ADB.  This package is used by the `Android TV <https://www.home-assistant.io/components/androidtv/>`_ integration in Home Assistant.


Installation
------------

.. code-block::

   pip install androidtv


To utilize the async version of this code, install the ``async`` extra:

.. code-block::

   pip install androidtv[async]


ADB Intents and Commands
------------------------

A collection of useful intents and commands can be found `here <https://gist.github.com/mcfrojd/9e6875e1db5c089b1e3ddeb7dba0f304>`_ (credit: mcfrojd).

Acknowledgments
---------------

This is based on `python-firetv <https://github.com/happyleavesaoc/python-firetv>`_ by happyleavesaoc and the `androidtv component for Home Assistant <https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py>`_ by a1ex4, and it depends on the Python packages `adb-shell <https://github.com/JeffLIrion/adb_shell>`_ (which is based on `python-adb <https://github.com/google/python-adb>`_) and `pure-python-adb <https://github.com/Swind/pure-python-adb>`_.
