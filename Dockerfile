FROM python:3.7

WORKDIR /pytest-gfix

COPY README.rst README.rst
COPY setup.py setup.py
COPY tox.ini tox.ini
COPY pytest_gfix.py pytest_gfix.py
COPY tests tests

RUN pip install tox flake8

CMD tox tests
