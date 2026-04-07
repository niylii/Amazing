PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt

all : run

install :
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt


run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)


clean:
	find . -type d -name "__pycache__" -exc rm -rf {} +
	find . -type d -name ".mypy_cache" -exc rm -rf {} +
	find . -name "*.pyc" -delete


lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: all install run debug clean lint lint-strict