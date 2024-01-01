help:
	@echo 'Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: dev
dev:
	$(MAKE) -j sourcedrun storerun updatedrun statusdrun

sourcedrun:
	@echo "sourced: localhost:8000"
	$(MAKE) -C sourced run

statusdrun:
	@echo "statusd: localhost:5000"
	$(MAKE) -C statusd run

storerun:
	@echo "MongoDB: localhost:27017"
	@echo "Redis: localhost:6379"
	$(MAKE) -C store run

updatedrun:
	$(MAKE) -C updated run

.PHONY: clean
clean:
	rm -rf $$(find -name __pycache__) venv
