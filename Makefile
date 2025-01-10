.PHONY: install test lint clean

install:
	pip install -e ".[dev]"

test:
	pytest

format:
	ruff format .
	ruff check . --fix


lint:
	ruff format . --check
	ruff check .
	mypy src

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete 