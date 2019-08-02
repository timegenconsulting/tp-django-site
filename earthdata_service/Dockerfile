ARG PYTHON_VERSION=3.6-slim-stretch

# Stage 0, instaling dev packages
FROM python:${PYTHON_VERSION} as builder
MAINTAINER Nebojsa Mrkic <mrkic.nebojsa@gmail.com>
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y install build-essential
WORKDIR /wheels
COPY ./requirements/ /wheels/requirements/
RUN pip install -U pip && pip wheel -r ./requirements/requirements.txt

# Stage 1, no dev packages on wheels
FROM python:${PYTHON_VERSION}
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install libgomp1

COPY --from=builder /wheels /wheels
RUN pip install -U pip \
       && pip install -r /wheels/requirements/requirements.txt \
                      -f /wheels \
       && rm -rf /wheels \
       && rm -rf /root/.cache/pip/*

# Copy code to docker
RUN mkdir -p /opt/app/AMSR
RUN mkdir -p /opt/app/logs
COPY ./ /opt/app/

# Copy the required source

# Initialize app
WORKDIR /opt/app


CMD ["/usr/local/bin/python", "main.py"]
