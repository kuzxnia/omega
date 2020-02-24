
.DEFAULT: help
help:
	@echo "make install"
	@echo "make run"
	@echo "make shell"
	@echo "make test"

install:
	pip install pipenv
	pipenv install --dev --pre
	pre-commit install -t pre-commit pre-push

run:
	pipenv run python manage.py runserver

shell:
	pipenv run python manage.py shell

test:
	pipenv run pytest -vv --color=yes --cov=omega --cov-report term-missing:skip-covered
