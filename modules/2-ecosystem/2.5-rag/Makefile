.PHONY: up run down clean

up:
	docker compose up -d
	@echo "Waiting for postgres to be ready..."
	@sleep 3

run:
	uv run rag_pipeline.py

down:
	docker compose down

clean:
	docker compose down -v
	rm -rf __pycache__ *.pyc
