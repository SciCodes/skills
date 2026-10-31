PYTHON ?= python3

.PHONY: lint validate check eval

lint:
	ruff check scripts tests
	yamllint -c .yamllint.yml .
	pymarkdown --config .pymarkdown.json scan README.md AGENTS.md skills tests

validate:
	$(PYTHON) scripts/validate.py
	$(PYTHON) -m unittest discover tests

check: lint validate

# Needs a model; set SCICODES_EVAL_CMD (see scripts/eval.py). May incur cost.
eval:
	$(PYTHON) scripts/eval.py
