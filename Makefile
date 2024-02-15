help:
	@echo '### Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: dev
dev:
	$(MAKE) storerun
	$(MAKE) -j sourcedrun statusdrun updatedrun

.PHONY: mindev
mindev:
	$(MAKE) storerun
	$(MAKE) statusdrun

sourcedrun:
	@echo "### sourced: localhost:8000"
	$(MAKE) -C sourced run

statusdrun:
	@echo "### statusd: localhost:5000"
	$(MAKE) -C statusd run

storerun:
	@echo "### postgres: localhost:5432"
	$(MAKE) -C store start

updatedrun:
	$(MAKE) -C updated run

.PHONY: seed
seed:
	$(MAKE) -C store start
	sleep 3
	$(MAKE) -C statusd seed

.PHONY: stop
stop:
	@echo "### stopping all services"
	$(MAKE) -C store stop

.INTERRUPT:
	@$(MAKE) stop
	@exit 1

.PHONY: clean
clean:
	$(MAKE) -C sourced clean
	$(MAKE) -C statusd clean
	$(MAKE) -C updated clean
	$(MAKE) -C store stop

.PHONY: delete
delete: clean
	$(MAKE) -C store delete
