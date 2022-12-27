.PHONY: build push

VERSION := latest
PLATFORMS = linux/amd64,linux/arm64

build:
	docker build --load -t mtik00/free-game-notifier:latest -f docker/Dockerfile --pull .
    ifneq ($(VERSION),latest)
	    docker build -t mtik00/free-game-notifier:$(VERSION) -f docker/Dockerfile --pull .
    endif

push:
	docker buildx build --platform ${PLATFORMS} -t mtik00/free-game-notifier:latest -f docker/Dockerfile --pull --push .
    ifneq ($(VERSION),latest)
	    docker buildx build --platform ${PLATFORMS} -t mtik00/free-game-notifier:$(VERSION) -f docker/Dockerfile --pull --push .
    endif

arm:
	docker buildx build --platform linux/arm64 -t mtik00/free-game-notifier:latest -f docker/Dockerfile --pull .

tag:
	git tag v$(shell poetry version -s)
