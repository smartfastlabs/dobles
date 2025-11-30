.PHONY: test
test: clean lint
	poetry run py.test -s -p no:dobles test

.PHONY: lint
lint:
	poetry run flake8 --extend-ignore E501 dobles test
	poetry run black .

.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -exec rm {} ';'

.PHONY: bootstrap
bootstrap:
	@pip install poetry 
	@poetry install --with lint,test,docs
	@poetry shell

.PHONY: docs
docs:
	@$(MAKE) -C docs html
