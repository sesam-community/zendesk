#!/bin/bash
# git update-index --add --chmod=+x docker_compose_push.sh
# echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
# docker-compose push

set -v
set -e
SLUG="$TRAVIS_REPO_SLUG"
REPO_NAME="${SLUG/#*\//}"
GIT_REPO_OWNER="${SLUG/%\/*/}"

#add similar line as below for each contributer that has GIT_REPO_OWVER and DOCKER_REPO_OWNER different
# DOCKER_REPO_OWNER=${GIT_REPO_OWNER/sesam-community/sesamcommunity}

if [ "$TRAVIS_BRANCH" == "master" ] && [ "$TRAVIS_PULL_REQUEST" == "false" ]
then
  DOCKER_REPO_TAG="development"
elif [ -n "$TRAVIS_TAG" ]
then
  DOCKER_REPO_TAG="$TRAVIS_TAG"
fi

echo Repo owner: $GIT_REPO_OWNER
echo $DOCKER_REPO_OWNER/$REPO_NAME:$DOCKER_REPO_TAG

# if [ -n "$DOCKER_REPO_TAG" ]
# then
#   docker build --label Commit="$TRAVIS_COMMIT" --label BuildNumber="$TRAVIS_BUILD_NUMBER" --label RepoSlug="$TRAVIS_REPO_SLUG" -t $DOCKER_REPO_OWNER/$REPO_NAME:$DOCKER_REPO_TAG .
#   docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
#   docker push $DOCKER_REPO_OWNER/$REPO_NAME:$DOCKER_REPO_TAG
# fi