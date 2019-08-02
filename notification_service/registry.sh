#!/bin/bash

DOCKER_REGISTRY=registry.gitlab.com/terraporta/django-site
REGISTRY_NAME=notification
PROJECT_VERSION=$(cat $1/notification/__init__.py | grep 'version' | sed 's:[^0-9\.]::g')

# build container
docker build --rm --force-rm -t $REGISTRY_NAME:$PROJECT_VERSION $1

# tag it
docker tag $REGISTRY_NAME:$PROJECT_VERSION $DOCKER_REGISTRY/$REGISTRY_NAME:$PROJECT_VERSION

# push images
docker push $DOCKER_REGISTRY/$REGISTRY_NAME:$PROJECT_VERSION
