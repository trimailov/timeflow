all: env install
dev: env pip-tools pip install

.PHONY: env
env:
	pyvenv env

.PHONY: pip-tools
pip-tools:
	env/bin/pip install --upgrade pip
	env/bin/pip install pip-tools

.PHONY: pip
pip: pip-compile
	env/bin/pip-sync requirements.txt

.PHONY: pip-compile
pip-compile:
	env/bin/pip-compile requirements.in

.PHONY: test
test:
	env/bin/python tests/tests.py

.PHONY: coverage
coverage:
	rm -rf htmlcov/ .coverage
	env/bin/coverage run --branch --omit='env/*' tests/tests.py
	env/bin/coverage report -m
	env/bin/coverage html
	@echo "Now you can use:"
	@echo "open htmlcov/index.html"

.PHONY: install
install:
	env/bin/pip install --editable .

.PHONY: uninstall
uninstall:
	env/bin/pip uninstall timeflow

.PHONY: tags
tags:
	ctags -R

.PHONY: clean
clean:
	rm -rf __pycache__ env timeflow.egg-info tags test_directory

.PHONY: remove_pyc
remove_pyc:
	find . -name "*.pyc" -delete
