migrate:
	uv run python manage.py collectstatic --noinput
	uv run python manage.py makemigrations
	uv run python manage.py migrate
	uv run python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User = get_user_model(); username = os.getenv('DJANGO_SUPERUSER_USER'); email = os.getenv('DJANGO_SUPERUSER_EMAIL'); password = os.getenv('DJANGO_SUPERUSER_PASSWORD'); User.objects.create_superuser(username, email, password) if not User.objects.filter(username=username).exists() else None"

dev:
	uv run python manage.py runserver

prod-run:
	uv run gunicorn -b 0.0.0.0:$(PORT) config.wsgi

lint:
	uv run ruff

lint-fix:
	uv run ruff check --fix