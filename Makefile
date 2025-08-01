migrate:
	uv run python manage.py collectstatic --noinput
	uv run python manage.py makemigrations
	uv run python manage.py migrate
	uv run python manage.py createsuperuser --noinput \
        --username $${DJANGO_SUPERUSER_USER} \
        --email $${DJANGO_SUPERUSER_EMAIL} \
        || echo "Superuser already exists or skipped"

dev:
	uv run python manage.py runserver

prod-run:
	uv run gunicorn -b 0.0.0.0:$(PORT) config.wsgi

lint:
	uv run ruff

lint-fix:
	uv run ruff check --fix