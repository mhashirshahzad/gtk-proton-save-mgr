# PYTHON=python3
VENV=.venv

PY=$(VENV)/bin/python

REQUIREMENTS=requirements.txt

run:
	python src/save-manager.py

deps: venv pip-bootstrap
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r $(REQUIREMENTS)

venv:
	@if [ ! -d $(VENV) ]; then \
		echo "Creating venv..."; \
		$(PYTHON) -m venv $(VENV); \
	fi

pip-bootstrap:
	@echo "Ensuring pip exists in venv..."
	@$(PY) -m ensurepip --upgrade || true

system-check:
	@python3 -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk" || \
	(echo "Missing GTK system deps" && exit 1)

clean:
	rm -rf $(VENV)
