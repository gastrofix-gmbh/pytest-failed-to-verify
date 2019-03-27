=======================
pytest-failed-to-verify
=======================

.. image:: https://img.shields.io/pypi/v/pytest-gfix.svg
    :target: https://pypi.org/project/pytest-gfix
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-gfix.svg
    :target: https://pypi.org/project/pytest-gfix
    :alt: Python versions

.. image:: https://travis-ci.org/gastrofix/pytest-gfix.svg?branch=master
    :target: https://travis-ci.org/amuehl/pytest-failed-to-verify
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/gastrofix/pytest-gfix?branch=master
    :target: https://ci.appveyor.com/project/gastrofix/pytest-gfix/branch/master
    :alt: See Build Status on AppVeyor

A plugin that enforces to get to the call phase, by enabling to only rerun the setup-phase on failure. We use it to deal with flaky tests ().

What's the idea behind it?
--------------------------

A python test consists of three phases (setup, call, teardown). Usually the call phase contains the actual tested business logic, and the outcome of this phase gives the most important result.
In order to get to the actual test-logic, the setup phase is used to provide the pre-conditions for the test and might be evem larger than the test.

Assuming that the flakiness of a test is evenly distributesd between the lines of code a test runs, having a large setup phase means an error due to flakyness is most likely to happen there. If that's the case a test fails but is leaving you with no relevant test-outcome: the actual test did not happen.

So re-running the setup phase is a mechanism that assures the code that tests the actual business logic is executed and gives you a valuable information about your test.

If the setup fails the result of a test will be `failed-to-verify` rather than failed.

I want to know more about it
----------------------------

We at gastrofix are also fighting the battle against flaky tests. Doing research we came across this very usefull and detailed article on how Dropbox is dealing with flaky tests in their CI [Dropbox: How we’re winning the battle against flaky tests](https://blogs.dropbox.com/tech/2018/05/how-were-winning-the-battle-against-flaky-tests/)

This plugin is a part of our adaption of their mechanism to deal with flaky tests.

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* Re-running the setup-phase on failure
* A new test-outcome: ``FAILED_TO_VERIFY`` if the test-logic was not executed

Credits
------------

Credits to https://github.com/pytest-dev as some of the code was taken and re-used from their plugin `pytest-rerunfailures <https://github.com/pytest-dev/pytest-rerunfailures>`_ which we used as a starting point to implelement the additionally needed functionality.

Known issues
------------

due to the similarity it does not work well together with pytest-rerunfailures, the functionality of pytest-rerunfailures is also working with this plugin tho.


Installation
------------

For now it can be installed using the following command:
``pip install -e git://github.com/amuehl/pytest-failed-to-verify.git#egg=pytest-failed-to-verify``

*Note: The plugin is not yet available via PyPi/pip.*


Usage
-----

Once installed the plugin re-runs the setup phase once in case of an error. It can be modified by the following envorinment variable:

``RERUN_SETUP = os.getenv('RERUN_SETUP_COUNT', 1)``

The additional pytest-rerunfailures functionality works like described [here]()

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-gfix" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/gastrofix/pytest-gfix/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
