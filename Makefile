DOCKER=podman

dist/soundboard_tg_bot-0.1.0-py3-none-any.whl:
	poetry build

image: dist/soundboard_tg_bot-0.1.0-py3-none-any.whl
	$(DOCKER) build .
