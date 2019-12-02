#!/bin/bash
# git update-index --add --chmod=+x docker_compose_push.sh
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker-compose push