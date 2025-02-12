#!/bin/sh

# Migrations and static files
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput

# Run server
exec "$@"
