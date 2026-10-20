.PHONY: setup run run-tokenizers run-generations run-pairs clean

# Uses the kit's .venv when it exists, so no need to activate it by hand.
PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

run: run-tokenizers

run-tokenizers:
	$(PYTHON) tokenizers_side_by_side.py $(TEXT)

run-generations:
	$(PYTHON) claude_generations.py

run-pairs:
	$(PYTHON) claude_pairs.py

clean:
	rm -rf .venv __pycache__ *.pyc
