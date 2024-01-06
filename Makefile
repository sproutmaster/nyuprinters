help:
	@echo '### Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: dev
dev:
	$(MAKE) -j sourcedrun statusdrun storerun updatedrun

.PHONY: mindev
mindev:
	$(MAKE) -j storerun statusdrun

sourcedrun:
	@echo "### sourced: localhost:8000"
	$(MAKE) -C sourced run

statusdrun:
	@echo "### statusd: localhost:5000"
	$(MAKE) -C statusd run

storerun:
	@echo "### Postgres: localhost:5432"
	$(MAKE) -C store run

updatedrun:
	$(MAKE) -C updated run

.PHONY: seed
seed:
	$(MAKE) -C store run
	$(MAKE) -C statusd seed

.PHONY: clean
clean:
	$(MAKE) -C sourced clean
	$(MAKE) -C statusd clean
	$(MAKE) -C updated clean

.PHONY: reset
reset: clean
	$(MAKE) -C store reset
