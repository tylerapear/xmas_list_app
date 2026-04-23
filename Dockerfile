FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/django_project

EXPOSE 80
EXPOSE 423

#CMD ["python", "manage.py", "runserver"]
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]