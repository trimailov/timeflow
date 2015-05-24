.PHONY: all
all: env install
	env/bin/pip install -r requirements.txt

.PHONY: env
env:
	pyvenv env

.PHONY: test
test:
	env/bin/python tests.py

.PHONY: coverage
coverage:
	rm -rf htmlcov/ .coverage
	env/bin/coverage run --branch --omit='env/*' tests.py
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

.PHONY: freeze
freeze:
	env/bin/pip freeze > requirements.txt

.PHONY: clean
clean:
	rm -rf __pycache__ env timeflow.egg-info tags test_directory
