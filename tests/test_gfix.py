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
    result = testdir.runpytest()
    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert '1 failed to verify' in result.stdout.str()


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
    result = testdir.runpytest()

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert '1 failed to verify' not in result.stdout.str()

    assert 'PASSED' not in result.stdout.str()
    assert '1 passed' in result.stdout.str()


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
    result = testdir.runpytest()

    assert 'FAILED TO VERIFY' not in result.stdout.str()
    assert '1 failed to verify' not in result.stdout.str()

    assert 'FAILED' not in result.stdout.str()
    assert '1 failed' in result.stdout.str()
