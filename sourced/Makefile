.PHONY: run
run:
	[ -d node_modules ] || $(MAKE) deps
	@echo "### Starting sourced"
	yarn run start

deps:
	@echo "### Installing sourced dependencies"
	yarn

.PHONY: clean
clean:
	@echo "### Cleaning sourced"
	rm -rf node_modules package-lock.json yarn.lock
