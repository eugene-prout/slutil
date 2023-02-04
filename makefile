test:
	python -m pytest tests/

coverage:
	coverage run  --source=slutil -m pytest tests/ 
	coverage html
	cd htmlcov && python -m http.server