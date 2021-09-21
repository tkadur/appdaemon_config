.PHONY: format
format:
	black apps

.PHONY: typecheck
typecheck:
	mypy apps

.PHONY: generate_stubs
generate_stubs:
	stubgen -p appdaemon -o stubs


.PHONY: setup
setup:
	apk add py3-scipy py3-numpy py3-cryptography
	pip install mypy black pylint pydantic
