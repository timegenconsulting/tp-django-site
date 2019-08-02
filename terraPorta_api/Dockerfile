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
COPY ./ /opt/app/

ENV DJANGO_SETTINGS_MODULE=terraPorta.settings.docker
WORKDIR /opt/app

# Collect our static media.
RUN python /opt/app/manage.py collectstatic --noinput

# Specify the command to run when the image is run.
CMD ["/usr/local/bin/uwsgi", "--ini", "/opt/app/conf/uwsgi.ini"]
