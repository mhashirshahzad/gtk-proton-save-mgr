VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

.PHONY: setup run clean install

# Setup virtual environment and install dependencies
setup:
	@echo "Setting up virtual environment..."
	python3 -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install pyyaml vdf pygobject
	@echo "Installing LSP..."
	$(PIP) install python-lsp-server
	@echo "✅ Setup complete! Run 'make run'"

# Install/update dependencies (run this if deps change)
install:
	$(PIP) install --upgrade pyyaml vdf pygobject

# Run the application
run:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Running setup..."; \
		$(MAKE) setup; \
	fi
	$(PYTHON) src/save-manager.py

# Clean everything
clean:
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Check installed packages
check:
	$(PIP) list
