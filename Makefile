###############################################
#
# External Enrollments commands.
#
###############################################

# Define PIP_COMPILE_OPTS=-v to get more information during make upgrade.
PIP_COMPILE = pip-compile --rebuild --upgrade $(PIP_COMPILE_OPTS)

.PHONY: requirements

.DEFAULT_GOAL := help

ifdef TOXENV
TOX := tox -- # to isolate each tox environment if TOXENV is defined.
endif

help: ## display this help message.
	@echo "Please use \`make <target>' where <target> is one of"
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

clean: ## delete most git-ignored files.
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	$(TOX) coverage erase
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

requirements: ## install environment requirements.
	pip install -r requirements/base.txt

upgrade: ## update the 'requirements/*.txt' files with the latest packages satisfying 'requirements/*.in'.
	pip install -qr requirements/pip-tools.txt
	$(PIP_COMPILE) -o requirements/pip-tools.txt requirements/pip-tools.in
	$(PIP_COMPILE) -o requirements/base.txt requirements/base.in
	$(PIP_COMPILE) -o requirements/quality.txt requirements/quality.in
	$(PIP_COMPILE) -o requirements/test.txt requirements/test.in
	$(PIP_COMPILE) -o requirements/tox.txt requirements/tox.in

python-quality-test: clean ## Check coding style with Pycodestyle and Pylint.
	$(TOX) pycodestyle --config=setup.cfg ./openedx_external_enrollments
	$(TOX) pylint ./openedx_external_enrollments --rcfile=./setup.cfg
	$(TOX) isort --check-only --recursive --diff ./openedx_external_enrollments

python-test: clean ## Run test suite.
	$(TOX) coverage run --source ./openedx_external_enrollments manage.py test
	$(TOX) coverage report -m --fail-under=83

install-dev-dependencies:
	pip install -r requirements/test.txt
	pip install -r requirements/quality.txt
	pip install -r requirements/tox.txt

run-tests: install-dev-dependencies python-test python-quality-test
