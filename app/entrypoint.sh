#!/bin/bash

# Wait for few minute and run db migraiton
while ! python manage.py migrate  2>&1; do
   echo "Migration is in progress status"
   sleep 3
done

echo "Django docker is fully configured successfully."


# Collect static files (if needed)
# python manage.py collectstatic --noinput

# Start the Django development server
python manage.py runserver 0.0.0.0:8000
