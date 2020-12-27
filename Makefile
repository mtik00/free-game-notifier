.PHONY: build push

PLATFORMS = linux/amd64,linux/arm64

build:
	docker build -t mtik00/free-game-notifier:latest -f docker/Dockerfile .

push:
	docker buildx build --platform ${PLATFORMS} -t mtik00/free-game-notifier:latest -f docker/Dockerfile --push .

arm:
	docker buildx build --platform linux/arm64 -t mtik00/free-game-notifier:latest -f docker/Dockerfile .
