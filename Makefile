

style-check:
	ruff check fake_data/ tests/
	ruff check --statistics fake_data/ tests/ 

format-check:
	ruff format --check fake_data/ tests/
