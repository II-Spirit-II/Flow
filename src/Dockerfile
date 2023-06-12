# Dockerfile
# Pull base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# collect static files
RUN python manage.py collectstatic --noinput

# run gunicorn
CMD gunicorn Flow.wsgi:application --bind 0.0.0.0:8000
