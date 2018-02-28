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
	env/bin/py.test timeflow/tests/tests.py

.PHONY: coverage
coverage:
	env/bin/py.test --cov=timeflow --cov-report=html timeflow/tests/tests.py

.PHONY: install
install:
	env/bin/pip install -r requirements.txt
	env/bin/pip install --editable .

.PHONY: uninstall
uninstall:
	env/bin/pip uninstall timeflow

.PHONY: tags
tags:
	ctags -R

.PHONY: clean
clean: remove_pyc
	rm -rf env timeflow.egg-info tags

.PHONY: remove_pyc
remove_pyc:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
