.DEFAULT_GOAL := all
isort = isort -rc werk24
autopep8 = autopep8 --max-line-length 120 --in-place --aggressive --aggressive -r  werk24

.PHONY: install
install:
	python -m pip install -U setuptools pip
	pip install -U -r requirements.txt

.PHONY: format
format:
	$(isort)
	$(autopep8)

.PHONY: push
push:
	nose2
	git add .
	git commit
	git push