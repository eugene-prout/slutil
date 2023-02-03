test:
	python -m pytest tests/

coverage:
	coverage run -m pytest tests/ 
	coverage report