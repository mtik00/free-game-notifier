.PHONY: image

image:
	docker build -t mtik00/steam-free-notifier:latest -f docker/Dockerfile .