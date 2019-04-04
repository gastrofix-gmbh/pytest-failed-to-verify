=======================
pytest-failed-to-verify
=======================

.. image:: https://img.shields.io/badge/license-MPL%202.0-blue.svg
   :target: https://github.com/pytest-dev/pytest-rerunfailures/blob/master/LICENSE
   :alt: License

.. image:: https://travis-ci.org/gastrofix-gmbh/pytest-failed-to-verify.svg?branch=master
    :target: https://travis-ci.org/gastrofix-gmbh/pytest-failed-to-verify
    :alt: See Build Status on Travis CI

.. image:: https://img.shields.io/pypi/v/pytest-failed-to-verify.svg
    :target: https://pypi.org/project/pytest-failed-to-verify
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-failed-to-verify.svg
    :target: https://pypi.org/project/pytest-failed-to-verify
    :alt: Python versions

A pytest plugin that helps better distinguishing real test failures from setup flakiness.


Features
--------

* Re-running only the setup-phase on failure
* Additional test-outcome: ``FAILED_TO_VERIFY`` if a failure happened in setup phase and prevented the actual test-logic from executing.

Installation
------------

For now it can be installed using the following command:
``pip install -e git://github.com/gastrofix-gmbh/pytest-failed-to-verify.git#egg=pytest-failed-to-verify``

*Note: The plugin is now available via PyPi/pip also.*
``pip install pytest-failed-to-verify``


Usage
-----
Based on the existing `pytest-rerunfailures <https://github.com/pytest-dev/pytest-rerunfailures>`_ plugin we added the following functionality:

Once installed the plugin provides an additional test outcome `failed-to-verify` in case a test fails in the setup-phase, additionaly you are able to control the amount of re-runs specifically for the setup phase:

``$ pytest --rerun-setup 1``


The core functionality of `pytest-rerunfailures <https://github.com/pytest-dev/pytest-rerunfailures>`_ can be used also with this plugin.

If you are interested in re-running the whole test you can use the following options globally:

``$ pytest --reruns 5 --reruns-delay 1``

or mark a single test as flaky like this:

.. code-block:: python

    @pytest.mark.flaky(reruns=5, reruns_delay=2)
    def test_example():
        import random
        assert random.choice([True, False])


What's the idea behind it?
--------------------------

A pytest test consists of three phases (setup, call, teardown). Usually only the call phase contains the actual tested business logic and the outcome of this phase gives the most valuable result.

The setup phase is used to provide the pre-conditions for the test and might be even larger than the test.

Assuming that the flakiness of a test is evenly distributed between the lines of code a test is executing, having a large setup phase means an error due to flakiness is most likely to happen there. If that's the case a test fails but is leaving you with no relevant test-outcome: the actual test did not happen. 

So if the setup fails the result of a test will be `failed-to-verify` rather than failed.

Additionally re-running only the setup phase is a mechanism that assures the code that is testing the actual business logic (call-phase) is actually executed and provides you a valid test outcome without suffering from a flaky setup phase. 


I want to know more about it
----------------------------

If you found this repo we wanted to let you know that we at gastrofix are also fighting the battle against flaky tests. Doing research we came across this very usefull and detailed article on how Dropbox is dealing with flaky tests in their CI (`Dropbox: How we’re winning the battle against flaky tests <https://blogs.dropbox.com/tech/2018/05/how-were-winning-the-battle-against-flaky-tests/>`_
).

This plugin is part of our approach of adapting their mechanism to deal with flaky tests.


Credits
------------

Credits to https://github.com/pytest-dev as some of the code was taken and re-used from their plugin `pytest-rerunfailures <https://github.com/pytest-dev/pytest-rerunfailures>`_ . We used it as a starting point to implelement the additionally needed functionality.

Known issues
------------

Because of the similarity it does not work well together with pytest-rerunfailures. If you still need to be able to rerun the complete test on case of an error you can do this as well using this plugin.

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/gastrofix/pytest-gfix/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
