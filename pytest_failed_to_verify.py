import time
import warnings

import pkg_resources
import pytest
from _pytest.resultlog import ResultLog
from _pytest.runner import runtestprotocol


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test setup
    if rep.when == "setup" and rep.failed:
        rep.outcome = 'failed'


def works_with_current_xdist():
    """Returns compatibility with installed pytest-xdist version.
    When running tests in parallel using pytest-xdist < 1.20.0, the first
    report that is logged will finish and terminate the current node rather
    rerunning the test. Thus we must skip logging of intermediate results under
    these circumstances, otherwise no test is rerun.
    """
    try:
        d = pkg_resources.get_distribution('pytest-xdist')
        return d.parsed_version >= pkg_resources.parse_version('1.20')
    except pkg_resources.DistributionNotFound:
        return None


# command line options
def pytest_addoption(parser):
    rerun_setup_group = parser.getgroup(
        "rerun-setup",
        "re-run failing test setup phase")
    rerun_setup_group._addoption(
        '--rerun-setup',
        action="store",
        dest="rerun_setup",
        type=int,
        default=0,
        help="number of times to re-run failed setup phase. defaults to 0.")

    rerun_failures_group = parser.getgroup(
        "rerunfailures",
        "re-run failing tests to eliminate flaky failures")
    rerun_failures_group._addoption(
        '--reruns',
        action="store",
        dest="reruns",
        type=int,
        default=0,
        help="number of times to re-run failed tests. defaults to 0.")
    rerun_failures_group._addoption(
        '--reruns-delay',
        action='store',
        dest='reruns_delay',
        type=float,
        default=0,
        help='add time (seconds) delay between reruns.'
    )


def pytest_configure(config):
    # add flaky marker
    config.addinivalue_line(
        "markers", "flaky(reruns=1, reruns_delay=0): mark test to re-run up "
                   "to 'reruns' times. Add a delay of 'reruns_delay' seconds "
                   "between re-runs.")


# making sure the options make sense
# should run before / at the begining of pytest_cmdline_main
def check_options(config):
    val = config.getvalue
    if not val("collectonly"):
        if config.option.reruns != 0:
            if config.option.usepdb:  # a core option
                raise pytest.UsageError("--reruns incompatible with --pdb")

    resultlog = getattr(config, '_resultlog', None)
    if resultlog:
        logfile = resultlog.logfile
        config.pluginmanager.unregister(resultlog)
        config._resultlog = RerunResultLog(config, logfile)
        config.pluginmanager.register(config._resultlog)


def _get_marker(item):
    try:
        return item.get_closest_marker("flaky")
    except AttributeError:
        # pytest < 3.6
        return item.get_marker("flaky")


def get_rerun_setup_count(item):
    rerun_setup = 0
    if item.session.config.option.rerun_setup:
        # default to the global setting
        rerun_setup = item.session.config.option.rerun_setup

    return rerun_setup


def get_reruns_count(item):
    rerun_marker = _get_marker(item)
    reruns = 0

    # use the marker as a priority over the global setting.
    if rerun_marker is not None:
        if "reruns" in rerun_marker.kwargs:
            # check for keyword arguments
            reruns = rerun_marker.kwargs["reruns"]
        elif len(rerun_marker.args) > 0:
            # check for arguments
            reruns = rerun_marker.args[0]
        else:
            reruns = 1
    elif item.session.config.option.reruns:
        # default to the global setting
        reruns = item.session.config.option.reruns

    return reruns


def get_reruns_delay(item):
    rerun_marker = _get_marker(item)

    if rerun_marker is not None:
        if "reruns_delay" in rerun_marker.kwargs:
            delay = rerun_marker.kwargs["reruns_delay"]
        elif len(rerun_marker.args) > 1:
            # check for arguments
            delay = rerun_marker.args[1]
        else:
            delay = 0
    else:
        delay = item.session.config.option.reruns_delay

    if delay < 0:
        delay = 0
        warnings.warn('Delay time between re-runs cannot be < 0. '
                      'Using default value: 0')

    return delay


def _remove_cached_results_from_failed_fixtures(item):
    """
    Note: remove all cached_result attribute from every fixture
    """
    cached_result = 'cached_result'
    fixture_info = getattr(item, '_fixtureinfo', None)
    for fixture_def_str in getattr(fixture_info, 'name2fixturedefs', ()):
        fixture_defs = fixture_info.name2fixturedefs[fixture_def_str]
        for fixture_def in fixture_defs:
            if hasattr(fixture_def, cached_result):
                result, cache_key, err = getattr(fixture_def, cached_result)
                if err:  # Deleting cached results for only failed fixtures
                    delattr(fixture_def, cached_result)


def _remove_failed_setup_state_from_session(item):
    """
    Note: remove all _prepare_exc attribute from every col in stack of _setupstate and cleaning the stack itself
    """
    prepare_exc = "_prepare_exc"
    setup_state = getattr(item.session, '_setupstate')
    for col in setup_state.stack:
        if hasattr(col, prepare_exc):
            delattr(col, prepare_exc)
    setup_state.stack = list()


def _clear_cache(parallel, report, item):
    if not parallel or works_with_current_xdist():
        # will rerun test, log intermediate result
        item.ihook.pytest_runtest_logreport(report=report)

    # cleanin item's cashed results from any level of setups
    _remove_cached_results_from_failed_fixtures(item)
    _remove_failed_setup_state_from_session(item)


def pytest_runtest_protocol(item, nextitem):
    """
    Note: when teardown fails, two reports are generated for the case, one for
    the test case and the other for the teardown error.
    """

    reruns = get_reruns_count(item)

    rerun_setup = get_rerun_setup_count(item)

    if reruns is None and rerun_setup is None:
        # global setting is not specified, and this test is not marked with
        # flaky
        return

    # while this doesn't need to be run with every item, it will fail on the
    # first item if necessary
    check_options(item.session.config)
    delay = get_reruns_delay(item)
    parallel = hasattr(item.config, 'slaveinput')
    item.execution_count = 0

    need_to_run = True
    while need_to_run:
        item.execution_count += 1
        item.ihook.pytest_runtest_logstart(nodeid=item.nodeid,
                                           location=item.location)
        reports = runtestprotocol(item, nextitem=nextitem, log=False)

        for report in reports:  # 3 reports: setup, call, teardown
            report.failed_to_verify = False
            if report.when == 'setup':
                report.rerun = item.execution_count - 1
                xfail = hasattr(report, 'wasxfail')
                if item.execution_count > rerun_setup and report.failed and not report.passed:
                    # last run and failure detected on setup
                    report.failed_to_verify = True
                    item.ihook.pytest_runtest_logreport(report=report)
                elif item.execution_count > rerun_setup or not report.failed or xfail:
                    # last run or no failure detected, log normally
                    item.ihook.pytest_runtest_logreport(report=report)
                else:
                    # failure detected and reruns not exhausted, since i < reruns
                    time.sleep(delay)
                    report.outcome = 'setup rerun'
                    _clear_cache(parallel, report, item)
                    break  # trigger rerun
            else:
                report.rerun = item.execution_count - 1
                xfail = hasattr(report, 'wasxfail')
                if item.execution_count > reruns or not report.failed or xfail:
                    # last run or no failure detected, log normally
                    item.ihook.pytest_runtest_logreport(report=report)
                else:
                    # failure detected and reruns not exhausted, since i < reruns
                    time.sleep(delay)
                    report.outcome = 'rerun'
                    _clear_cache(parallel, report, item)
                    break  # trigger rerun
        else:
            need_to_run = False

        item.ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)

    return True


def pytest_report_teststatus(report):
    """Adapted from https://pytest.org/latest/_modules/_pytest/skipping.html
    """
    if report.outcome == 'rerun':
        return 'rerun', 'R', ('RERUN', {'yellow': True})
    if report.outcome == 'setup rerun':
        return 'setup rerun', 'SR', ('SETUP RERUN',
                                     {'yellow': True})

    if report.failed_to_verify:
        return 'failed to verify', 'F2V', ('FAILED TO VERIFY',
                                 {'red': True})


def pytest_terminal_summary(terminalreporter):
    """Adapted from https://pytest.org/latest/_modules/_pytest/skipping.html
    """
    tr = terminalreporter
    if not tr.reportchars:
        return

    failed_to_verify = tr.stats.get("failed to verify")
    lines = []
    for char in tr.reportchars:
        if char in 'rR':
            show_rerun(terminalreporter, lines)

    if failed_to_verify:
        for rep in failed_to_verify:
            pos = rep.nodeid
            lines.append("FAILED TO VERIFY %s" % (pos,))
            lines.append(rep.longreprtext)

    if lines:
        tr._tw.sep("=", "rerun test summary info")
        for line in lines:
            tr._tw.line(line)


def show_rerun(terminalreporter, lines):
    rerun = terminalreporter.stats.get("rerun")
    if rerun:
        for rep in rerun:
            pos = rep.nodeid
            lines.append("RERUN %s" % (pos,))


class RerunResultLog(ResultLog):
    def __init__(self, config, logfile):
        ResultLog.__init__(self, config, logfile)

    def pytest_runtest_logreport(self, report):
        """
        Adds support for rerun report fix for issue:
        https://github.com/pytest-dev/pytest-rerunfailures/issues/28
        """
        if report.when != "call" and report.passed:
            return
        res = self.config.hook.pytest_report_teststatus(report=report)
        code = res[1]
        if code == 'x':
            longrepr = str(report.longrepr)
        elif code == 'X':
            longrepr = ''
        elif report.passed:
            longrepr = ""
        elif report.failed:
            longrepr = str(report.longrepr)
        elif report.skipped:
            longrepr = str(report.longrepr[2])
        elif report.outcome == 'rerun':
            longrepr = str(report.longrepr)

        self.log_outcome(report, code, longrepr)
