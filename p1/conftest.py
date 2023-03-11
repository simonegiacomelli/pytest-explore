# def pytest_ignore_collect(collection_path, path, config):
#     print('p1 pytest_ignore_collect', collection_path, path, config)
#     return True

import re
import sys
import traceback

import pytest


def pytest_sessionstart(session):
    pluginmanager = session.config.pluginmanager
    if not session.config.option.collectonly:
        pluginmanager.unregister(name='python')

    capmanager = pluginmanager.getplugin('capturemanager')
    capmanager.suspend_global_capture(in_=True)

    capmanager.resume_global_capture()

    session.stbt_node = 'node-custom'
    session.stbt_run_prep = 'j-custom'


def pytest_addoption(parser):
    pass


def pytest_collect_file(file_path, path, parent):
    if path.ext == ".py":
        return StbtCollector.from_parent(parent, path=file_path)
    else:
        return None


pass


class StbtCollector(pytest.File):
    def collect(self):

        with open(self.fspath.strpath) as f:
            # We implement our own parsing to avoid import stbt ImportErrors
            for n, line in enumerate(f):
                m = re.match(r'^def\s+(test_[a-zA-Z0-9_]*)', line)
                if m:
                    yield StbtRemoteTest.from_parent(self, filename=self.fspath, testname=m.group(1), line_number=n + 1)


pass


class StbtRemoteTest(pytest.Item):
    def __init__(self, parent, filename, testname, line_number):
        print(f'StbtRemoteTest {parent} {filename} {testname}')
        super(StbtRemoteTest, self).__init__(testname, parent)
        self._filename = filename
        self._testname = testname
        self._line_number = line_number

    def __repr__(self):
        return "StbtRemoteTest(%r, %r, %r)" % (
            self._filename, self._testname, self._line_number)


    def runtest(self):
        try:
            # self.session.stbt_args.test_cases = ["%s::%s" % (self._filename, self._testname)]
            if 'will_fail' in self._testname:
                raise Exception('Synthetic exception!')
        finally:
            # self.session.stbt_args.test_cases = None
            pass

    def reportinfo(self):
        return self.fspath, self._line_number, ""
