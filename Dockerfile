FROM python:3.8-slim as base

FROM base
COPY . /app
WORKDIR app
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app_runner.py"]
