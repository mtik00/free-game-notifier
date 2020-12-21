.PHONY: build push

PLATFORMS = linux/amd64,linux/arm64

build:
	docker build -t mtik00/steam-free-notifier:latest -f docker/Dockerfile .

push:
	docker buildx build --platform ${PLATFORMS} -t mtik00/steam-free-notifier:latest --target compile -f docker/Dockerfile --push .