

PYTHON_MATRIX_VERSION ?= local

.PHONY: style-check format-check unit-test unit-test-coverage

style-check:
	ruff check --output-format=github fake_data/ tests/
	ruff check --statistics fake_data/ tests/ 

format-check:
	ruff format --check fake_data/ tests/

unit-test:
	pytest ./tests

unit-test-coverage:
	pytest --cov=./fake_data --cov-report=term-missing
	# coverage report --skip-empty 
