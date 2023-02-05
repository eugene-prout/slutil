test:
	poetry run python -m pytest tests/

coverage:
	poetry run coverage run  --source=slutil -m pytest tests/ 
	poetry run coverage html
	cd htmlcov && poetry run python -m http.server