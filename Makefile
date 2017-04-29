.PHONY: help
help: install
	python -m cah -h

.PHONY: run
run: install
	python -m cah

.PHONY: install
install: build
	pip install --upgrade -e .

.PHONY: build
build:
	-mkdir ./cah
	cp -R ./cah-source/* ./cah
	coconut setup.coco -s
	coconut cah -s -j sys

.PHONY: setup
setup:
	pip install coconut-develop

.PHONY: clean
clean:
	rm -rf ./dist ./build
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

.PHONY: wipe
wipe: clean
	find . -name '*.py' -delete
	rm -rf ./cah
