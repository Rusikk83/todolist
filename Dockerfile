FROM python:3.10-slim
RUN apt update && apt install -y gcc cmake libpq-dev python-dev
WORKDIR /code
COPY requirements.txt .
# COPY .env .
RUN pip install -r requirements.txt

COPY todolist todolist/
CMD ["python", "todolist/manage.py", "runserver", "0.0.0.0:8000"]