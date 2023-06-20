# Dockerfile
# Pull base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies for locale
RUN apt-get clean && apt-get update && apt-get install -y locales

# Uncomment the locale in the file
RUN sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen

# Generate the locale
RUN locale-gen

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# run gunicorn
CMD gunicorn Flow.wsgi:application --bind 0.0.0.0:8000