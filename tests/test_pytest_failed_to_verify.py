pytest_plugins = 'pytester'


def temporary_failure():
    return "raise Exception('Failure')"


def test_fail_to_verify_if_setup_fails(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            {0}

        def test_example_1():
            assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest('--rerun-setup', '1')
    assert 'FAILED TO VERIFY' in result.stdout.str()
    assert '1 failed to verify' in result.stdout.str()
    assert '1 setup rerun' in result.stdout.str()
    assert result.ret == 1


def test_fail_to_verify_if_setup_fails_multiple_times(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            {0}

        def test_example_1():
            assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest('--rerun-setup', '2')
    assert 'FAILED TO VERIFY' in result.stdout.str()
    assert '1 failed to verify' in result.stdout.str()
    assert '2 setup rerun' in result.stdout.str()
    assert result.ret == 1


def test_fail_setup_and_pass(testdir):
    testdir.makepyfile(
        """
        import pytest
        COUNT = 0
        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            global COUNT
            if COUNT == 0:
                COUNT += 1
                assert False
            else:
                assert True

        def test_example_1():
            assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest('--rerun-setup', '1')
    assert 'failed to verify' not in result.stdout.str()
    assert '1 setup rerun' in result.stdout.str()
    assert '1 passed' in result.stdout.str()
    assert result.ret == 0


def test_passed_in_output_if_setup_and_test_successfull(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            pass

        def test_example_1():
            assert True
        """
    )
    result = testdir.runpytest('--rerun-setup', '1')

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert '1 failed to verify' not in result.stdout.str()

    assert 'PASSED' not in result.stdout.str()
    assert '1 passed' in result.stdout.str()
    assert result.ret == 0


def test_failed_in_output_on_error_in_test_logic(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            pass

        def test_example_1():
            assert False
        """
    )
    result = testdir.runpytest('--rerun-setup', '1')

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert '1 failed to verify' not in result.stdout.str()

    assert 'setup rerun' not in result.stdout.str()

    assert 'FAILED' not in result.stdout.str()
    assert '1 failed' in result.stdout.str()
    assert result.ret == 1


def test_rerun_by_decorator(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            pass

        @pytest.mark.flaky(reruns=2)
        def test_example_1():
            assert False
        """
    )
    result = testdir.runpytest('--rerun-setup', '1')

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()

    assert '1 failed' in result.stdout.str()
    assert '2 rerun' in result.stdout.str()
    assert result.ret == 1


def test_rerun_by_decorator_flaky_test(testdir):
    testdir.makepyfile(
        """
        import pytest
        COUNT = 0
        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            pass

        @pytest.mark.flaky(reruns=2)
        def test_example_1():
            global COUNT
            if COUNT < 2:
                COUNT += 1
                assert False
            else:
                assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest('--rerun-setup', '1')

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()

    assert '1 passed' in result.stdout.str()
    assert '2 rerun' in result.stdout.str()
    assert result.ret == 0


def test_rerun_by_decorator_flaky_test_and_flaky_setup(testdir):
    testdir.makepyfile(
        """
        import pytest
        COUNT = 0
        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            global COUNT
            if COUNT == 0:
                COUNT += 1
                assert False
            else:
                assert True

        @pytest.mark.flaky(reruns=2)
        def test_example_1():
            global COUNT
            if COUNT < 2:
                COUNT += 1
                assert False
            else:
                assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest('--rerun-setup', '1')

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()

    assert '1 passed' in result.stdout.str()
    assert '1 setup rerun' in result.stdout.str()
    assert '1 rerun' in result.stdout.str()
    assert result.ret == 0


def test_skipped(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            assert True

        @pytest.mark.skip(reason='Reason why skipped')
        def test_example_1():
            assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest('--rerun-setup', '1')

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()

    assert '1 skipped' in result.stdout.str()
    assert result.ret == 0


def test_xfail(testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            assert True

        @pytest.mark.xfail(reason='Reason why skipped')
        def test_example_1():
            assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest('--rerun-setup', '1')

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()

    assert '1 xpassed' in result.stdout.str()
    assert result.ret == 0
