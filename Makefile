# ---- Config ----
PYTHON := python
APP := src/save-manager.py
VENV := .venv

# ---- Default ----
.PHONY: run
run:
	$(PYTHON) $(APP)

# ---- Virtual Environment ----
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -U pip
	. $(VENV)/bin/activate && pip install pyyaml vdf rich simple-colors

# ---- Run with venv ----
.PHONY: run-venv
run-venv:
	. $(VENV)/bin/activate && $(PYTHON) $(APP)

# ---- Clean ----
.PHONY: clean
clean:
	rm -rf __pycache__ */__pycache__ *.pyc

# ---- Full reset ----
.PHONY: reset
reset: clean
	rm -rf $(VENV)
