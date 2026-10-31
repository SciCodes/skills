PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
.DEFAULT_GOAL := check

.PHONY: setup lint validate check eval

setup: $(VENV)/.dev-installed

$(VENV)/.dev-installed: requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt
	touch $@

lint: setup
	$(VENV)/bin/ruff check scripts tests
	$(VENV)/bin/yamllint -c .yamllint.yml .
	$(VENV)/bin/pymarkdown --config .pymarkdown.json scan README.md AGENTS.md skills tests

validate: setup
	$(VENV_PYTHON) scripts/validate.py
	$(VENV_PYTHON) -m unittest discover tests

check: lint validate

# Needs a model; set SCICODES_EVAL_CMD (see scripts/eval.py). May incur cost.
eval: setup
	$(VENV_PYTHON) scripts/eval.py
