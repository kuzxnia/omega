
.DEFAULT: help
help:
	@echo "make install"
	@echo "make run_api"
	@echo "make run_celery"
	@echo "make shell"
	@echo "make test"

install:
	pip install pipenv
	pip install black==18.9b0
	pipenv install --dev
	pipenv run pre-commit install & pre-commit install -t pre-push

run_api:
	pipenv run python manage.py runserver

run_celery:
	pipenv run python manage.py celery runserver

shell:
	pipenv run python manage.py shell

test:
	pipenv run pytest -vv --color=yes --cov=omega --cov-report term-missing:skip-covered
