.PHONY: run
run:
	@echo "### Starting DB services"
	docker compose -f docker-compose-dev.yml up -d

.PHONY: stop
stop:
	@echo "### Stopping DB services"
	docker compose -f docker-compose-dev.yml stop

.PHONY: clean
clean:
	@echo "### Cleaning DB services"
	docker compose -v -f docker-compose-dev.yml down
