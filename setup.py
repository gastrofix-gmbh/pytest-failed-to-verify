#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-failed-to-verify',
    version='0.1.5',
    author='Gastrofix GmbH',
    author_email='tech@gastrofix.com',
    maintainer='Gastrofix GmbH',
    maintainer_email='tech@gastrofix.com',
    license='MPL',
    url='https://github.com/gastrofix-gmbh/pytest-failed-to-verify',
    description='A pytest plugin that helps better distinguishing real test failures from setup flakiness.',
    long_description=read('README.rst'),
    py_modules=['pytest_failed_to_verify'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=['pytest>=4.1.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ],
    entry_points={
        'pytest11': [
            'failed-to-verify = pytest_failed_to_verify',
        ],
    },
)
