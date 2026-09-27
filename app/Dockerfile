FROM python:3.13-slim

WORKDIR /app

COPY app.py .
COPY app_crash.py .

EXPOSE 8000

CMD ["python", "app.py"]