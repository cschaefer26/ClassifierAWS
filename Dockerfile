ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION}-slim as base

FROM base as builder

RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt

RUN pip install --prefix=/install -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local

RUN mkdir /app
WORKDIR /app
COPY classifier classifier
COPY app_runner.py .
COPY logging-config.yaml .

EXPOSE 80

ENTRYPOINT ["python", "app_runner.py"]
