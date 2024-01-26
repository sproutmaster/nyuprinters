help:
	@echo '### Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: run
run:
	[ -d node_modules ] || $(MAKE) deps
	@echo "### Starting sourced"
	yarn run start

deps:
	@echo "### Installing sourced dependencies"
	yarn


.PHONY: dkbuild
dkbuild:
	@echo "### Building sourced docker image"
	docker build -t sourced:latest .


.PHONY: clean
clean:
	@echo "### Cleaning sourced"
	rm -rf node_modules package-lock.json yarn.lock

