PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
.DEFAULT_GOAL := check

.PHONY: setup lint lint-check validate check eval

setup: $(VENV)/.dev-installed

$(VENV)/.dev-installed: requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt
	touch $@

lint: setup
	$(VENV)/bin/ruff check --fix scripts tests
	$(VENV)/bin/ruff format scripts tests
	# PyMarkdown returns 3 when it successfully fixes files.
	$(VENV)/bin/pymarkdown --enable-extensions front-matter --config .pymarkdown.json fix --recurse README.md AGENTS.md skills tests || { lint_status=$$?; test "$$lint_status" -eq 3 || exit "$$lint_status"; }
	$(MAKE) lint-check

lint-check: setup
	$(VENV)/bin/ruff check scripts tests
	$(VENV)/bin/ruff format --check scripts tests
	$(VENV)/bin/yamllint -c .yamllint.yml .
	$(VENV)/bin/pymarkdown --enable-extensions front-matter --config .pymarkdown.json scan --recurse README.md AGENTS.md skills tests

validate: setup
	$(VENV_PYTHON) scripts/validate.py
	$(VENV_PYTHON) -m unittest discover tests

check: lint-check validate

# Needs a model; set SCICODES_EVAL_CMD (see scripts/eval.py). May incur cost.
eval: setup
	$(VENV_PYTHON) scripts/eval.py
