PYTHON := python3.10

help:
	@echo '### Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: run
run: venv
	./.venv/bin/python3 main.py

.PHONY: venv
venv:
	@if [ ! -d .venv ]; then \
  		echo "### Creating virtual environment"; \
		$(PYTHON) -m venv .venv; \
		./.venv/bin/python3 -m pip install --upgrade pip; \
		./.venv/bin/pip install -r requirements.txt; \
#		./.venv/bin/activate; \
	fi

.PHONY: seed
seed: venv
	./.venv/bin/python3 seed/seeder.py

.PHONY: req
requirements: venv
	pip-compile --quiet --upgrade requirements.txt

.PHONY: clean
clean:
	@echo "### Deleting virtual environment"
	rm -rf $$(find -name __pycache__) .venv
