
.PHONY: style-check format-check unit-test

style-check:
	ruff check --output-format=github fake_data/ tests/
	ruff check --statistics fake_data/ tests/ 

format-check:
	ruff format --check fake_data/ tests/

unit-test:
	pytest --junitxml=junit/test-results.xml --cov=fake_data --cov-report=xml --cov-report=html