.PHONE: format
format:
	black apps

.PHONY: typecheck
typecheck:
	mypy apps

.PHONY: generate_stubs
generate_stubs:
	stubgen -p appdaemon -o stubs