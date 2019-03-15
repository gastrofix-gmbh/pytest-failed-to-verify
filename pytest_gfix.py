import pytest


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test setup
    if rep.when == "setup" and rep.failed:
        rep.outcome = 'failed to verify'


def pytest_report_teststatus(report):
    """Adapted from https://pytest.org/latest/_modules/_pytest/skipping.html
    """
    if report.outcome == 'failed to verify':
        return 'failed to verify', 'F2V', ('FAILED TO VERIFY',
                                           {'yellow': True})


def pytest_terminal_summary(terminalreporter):
    """Adapted from https://pytest.org/latest/_modules/_pytest/skipping.html
    """
    tr = terminalreporter
    if not tr.reportchars:
        return

    lines = []
    for char in tr.reportchars:
        if char in 'fF':
            show_failed_to_verify(terminalreporter, lines)
    if lines:
        tr._tw.sep("=", "rerun test summary info")
        for line in lines:
            tr._tw.line(line)


def show_failed_to_verify(terminalreporter, lines):
    failed_to_verify = terminalreporter.stats.get("failed to verify")
    if failed_to_verify:
        for rep in failed_to_verify:
            pos = rep.nodeid
            lines.append("FAILED TO VERIFY %s" % (pos,))
