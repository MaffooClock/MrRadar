PYTHON = /usr/bin/env python3
PYTHON_M = ${PYTHON} -m
PIP_INSTALL = ${PYTHON_M} pip install

.PHONY = help install install_test test clean

.DEFAULT_GOAL = help

help:
	@echo "------------------------ HELP --------------------------"
	@echo "To install required dependencies:"
	@echo "    make install"
	@echo
	@echo "To install optional dependencies needed to run tests:"
	@echo "    make install_test"
	@echo
	@echo "To run tests (after installing optional dependencies):"
	@echo "    make test"
	@echo
	@echo "To clean out the Python bytecode cache:"
	@echo "    make clean"
	@echo "--------------------------------------------------------"

install:
	${PIP_INSTALL} .

install_test:
	${PIP_INSTALL} ".[test]"

test:
	${PYTHON_M} pytest --color=auto --code-highlight=yes --cov=mr_radar --cov-report=xml --junitxml=junit.xml

clean:
	rm -rf mr_radar/__pycache__
