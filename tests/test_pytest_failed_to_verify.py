import pytest

pytest_plugins = 'pytester'


def temporary_failure():
    return "raise Exception('Failure')"


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_fail_to_verify_if_setup_fails(pytest_command, testdir):
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
    result = testdir.runpytest(*pytest_command.split())
    assert '1 setup rerun' in result.stdout.str()
    assert '1 failed to verify' in result.stdout.str()
    assert 'FAILED TO VERIFY' in result.stdout.str()
    assert 'Exception: Failure' in result.stdout.str()
    assert result.ret == 1


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 2', '--rerun-setup 2 -x'])
def test_fail_to_verify_if_setup_fails_multiple_times(pytest_command, testdir):
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
    result = testdir.runpytest(*pytest_command.split())
    assert '2 setup rerun' in result.stdout.str()
    assert '1 failed to verify' in result.stdout.str()
    assert 'FAILED TO VERIFY' in result.stdout.str()
    assert 'Exception: Failure' in result.stdout.str()
    assert result.ret == 1


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_fail_setup_and_pass(pytest_command, testdir):
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
        """
    )
    result = testdir.runpytest(*pytest_command.split())
    assert 'failed to verify' not in result.stdout.str()
    assert '1 setup rerun' in result.stdout.str()
    assert '1 passed' in result.stdout.str()
    assert result.ret == 0


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_passed_in_output_if_setup_and_test_successfull(pytest_command, testdir):
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
    result = testdir.runpytest(*pytest_command.split())

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert '1 failed to verify' not in result.stdout.str()
    assert 'PASSED' not in result.stdout.str()

    assert '1 passed' in result.stdout.str()
    assert result.ret == 0


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_failed_in_output_on_error_in_test_logic(pytest_command, testdir):
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
    result = testdir.runpytest(*pytest_command.split())
    assert 'setup rerun' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()
    assert '1 failed' in result.stdout.str()

    assert 'falied to verify' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()
    assert 'passed' not in result.stdout.str()
    assert result.ret == 1


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_skipped(pytest_command, testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            assert True

        @pytest.mark.skip(reason='Reason why skipped')
        def test_example_1():
            assert True
        """
    )
    result = testdir.runpytest(*pytest_command.split())

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()

    assert '1 skipped' in result.stdout.str()
    assert result.ret == 0


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_skipped_and_setup_fail(pytest_command, testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            assert False

        @pytest.mark.skip(reason='Reason why skipped')
        def test_example_1():
            assert True
        """
    )
    result = testdir.runpytest(*pytest_command.split())

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()

    assert '1 skipped' in result.stdout.str()
    assert result.ret == 0


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_xfail(pytest_command, testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            assert True

        @pytest.mark.xfail(reason='Reason why skipped')
        def test_example_1():
            assert True
        """
    )
    result = testdir.runpytest(*pytest_command.split())

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert 'failed to verify' not in result.stdout.str()
    assert 'FAILED' not in result.stdout.str()
    assert 'setup rerun' not in result.stdout.str()

    assert '1 xpassed' in result.stdout.str()
    assert result.ret == 0


@pytest.mark.parametrize("pytest_command", ['--rerun-setup 1', '--rerun-setup 1 -x'])
def test_xfail_and_setup_failure(pytest_command, testdir):
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture(scope='function', autouse=True)
        def function_setup_teardown():
            {0}

        @pytest.mark.xfail(reason='Reason why skipped')
        def test_example_1():
            assert True
        """.format(temporary_failure())
    )
    result = testdir.runpytest(*pytest_command.split())

    assert 'FAILED TO VERIFY' in result.stdout.str()
    assert 'failed to verify' in result.stdout.str()
    assert 'setup rerun' in result.stdout.str()
    assert '1 failed to verify' in result.stdout.str()
    assert 'Exception: Failure' in result.stdout.str()

    assert result.ret == 1
