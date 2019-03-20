import pytest
import os
from _pytest.runner import runtestprotocol
from _pytest.main import EXIT_TESTSFAILED


reruns = os.getenv('RERUN_SETUP_COUNT', 1)


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
    if report.when == 'setup':
        if report.outcome == 'failed to verify':
            return 'failed to verify', 'F2V', ('FAILED TO VERIFY',
                                               {'red': True})
        if report.outcome == 'setup rerun':
            return 'setup rerun', 'SR', ('SETUP RERUN',
                                         {'yellow': True})


def pytest_terminal_summary(terminalreporter):
    """Adapted from https://pytest.org/latest/_modules/_pytest/skipping.html
    """
    tr = terminalreporter
    if not tr.reportchars:
        return
    failed_to_verify = tr.stats.get("failed to verify")
    lines = []
    if failed_to_verify:
        tr._session.exitstatus = EXIT_TESTSFAILED
        for rep in failed_to_verify:
            pos = rep.nodeid
            lines.append("FAILED TO VERIFY %s" % (pos,))
    if lines:
        tr._tw.sep("=", "failed to verify summary info")
        for line in lines:
            tr._tw.line(line)


def pytest_runtest_protocol(item, nextitem):
    execution_count = 0
    while True:
        execution_count += 1
        item.ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
        reports = runtestprotocol(item, nextitem)
        for report in reports:
            if execution_count > reruns:
                item.ihook.pytest_runtest_logreport(report=report)
            else:
                if report.when == 'setup' and not report.passed:
                    report.outcome = 'setup rerun'
                    item.ihook.pytest_runtest_logreport(report=report)
                    break
                else:
                    item.ihook.pytest_runtest_logreport(report=report)
        else:
            return True
