.PHONY: build push

VERSION := latest
PLATFORMS = linux/amd64,linux/arm64

build:

	docker buildx build -t mtik00/free-game-notifier:latest -f docker/Dockerfile .
    ifneq ($(VERSION),latest)
	    docker buildx build -t mtik00/free-game-notifier:$(VERSION) -f docker/Dockerfile .
    endif

push:
	docker buildx build --platform ${PLATFORMS} -t mtik00/free-game-notifier:latest -f docker/Dockerfile --push .
    ifneq ($(VERSION),latest)
	    docker buildx build --platform ${PLATFORMS} -t mtik00/free-game-notifier:$(VERSION) -f docker/Dockerfile --push .
    endif

arm:
	docker buildx build --platform linux/arm64 -t mtik00/free-game-notifier:latest -f docker/Dockerfile .
