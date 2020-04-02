export DOCKER_REPO_NAME ?= $(subst digitalmarketplace-,,$(notdir $(shell pwd)))
export RELEASE_NAME ?= $(shell git describe)

.PHONY: docker-build
## Build a Docker image for this app
docker-build:
	@echo "Building a docker image for digitalmarketplace/${DOCKER_REPO_NAME}:${RELEASE_NAME}..."
	docker build -t digitalmarketplace/${DOCKER_REPO_NAME} --build-arg release_name=${RELEASE_NAME} .
	docker tag digitalmarketplace/${DOCKER_REPO_NAME} digitalmarketplace/${DOCKER_REPO_NAME}:${RELEASE_NAME}

.PHONY: docker-push
## Push the Docker image for this app to Docker Hub
docker-push:
	docker push digitalmarketplace/${DOCKER_REPO_NAME}:${RELEASE_NAME}