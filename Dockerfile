# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/darshandevelopes/TalentTrailAPI.git /usr/src/app
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN pip install wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Collect static files
RUN python manage.py collectstatic --noinput

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define default command to start the app container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "TalentTrailAPI.wsgi:application"]
