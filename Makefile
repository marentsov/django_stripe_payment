migrate:
	uv run python manage.py collectstatic --noinput
	uv run python manage.py makemigrations
	uv run python manage.py migrate
	uv run python manage.py shell -c "\
from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.create_superuser( \
    '$${DJANGO_SUPERUSER_USER}', \
    '$${DJANGO_SUPERUSER_EMAIL}', \
    '$${DJANGO_SUPERUSER_PASSWORD}' \
) if not User.objects.filter(username='$${DJANGO_SUPERUSER_USER}').exists() else None\
"
dev:
	uv run python manage.py runserver

prod-run:
	uv run gunicorn -b 0.0.0.0:$(PORT) config.wsgi

lint:
	uv run ruff

lint-fix:
	uv run ruff check --fix