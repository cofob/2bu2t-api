.PHONY: lint
lint:
	mypy --install-types --non-interactive .
	flake8 .

.PHONY: style
style:
	pycln . -c --config setup.cfg
	black . --check
	isort . -c

.PHONY: test
test: lint style
	pytest .

.PHONY: format
format:
	pycln . --config setup.cfg
	black .
	isort .
