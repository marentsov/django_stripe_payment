import os
from django.contrib.auth import get_user_model


def create_admin():
    User = get_user_model()
    username = os.getenv('DJANGO_SUPERUSER_USER', 'admin')  # fallback to 'admin'
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser {username} created")
    else:
        print("Superuser already exists")


if __name__ == "__main__":
    create_admin()