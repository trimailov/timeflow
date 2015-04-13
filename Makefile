.PHONY: all
all: env
	env/bin/pip install -r requirements.txt

.PHONY: env
env:
	pyvenv env

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
	rm -rf __pycache__ env timeflow.egg-info tags
