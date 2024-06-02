FROM python:3.10.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY . .

COPY requirements.txt .
RUN pip install wheel && pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader punkt stopwords

RUN python manage.py migrate && python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "TalentTrailAPI.wsgi:application"]