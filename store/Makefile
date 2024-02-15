help:
	@echo '### Available make targets:'
	@grep PHONY: Makefile | cut -d: -f2 | sed '1d;s/^/make/'

.PHONY: start
start:
	@echo "### Starting DB services"
	docker compose -f docker-compose-dev.yml up -d

.PHONY: stop
stop:
	@echo "### Stopping DB services"
	docker compose -f docker-compose-dev.yml stop

.PHONY: delete
delete:
	@echo "### Deleting DB services"
	docker compose -f docker-compose-dev.yml down -v
