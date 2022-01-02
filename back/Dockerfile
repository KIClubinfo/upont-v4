# syntax=docker/dockerfile:1
FROM python:3.9.6-bullseye
ENV PYTHONUNBUFFERED=1
ENV VENV=/opt/venv
RUN python3 -m venv $VENV
ENV PATH="$VENV/bin:$PATH"

ENV PATH="$PATH:/src/bin"
RUN apt-get install -y chromium-browser

WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
