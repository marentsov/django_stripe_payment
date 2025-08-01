migrate:
	uv run python manage.py collectstatic --noinput
	uv run python manage.py makemigrations
	uv run python manage.py migrate
	DJANGO_SETTINGS_MODULE=config.settings uv run python create_admin.py

dev:
	uv run python manage.py runserver

prod-run:
	uv run python -m gunicorn --bind 0.0.0.0:8000 config.wsgi

lint:
	uv run ruff

lint-fix:
	uv run ruff check --fix


tests:
	uv run pytest
