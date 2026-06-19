.PHONY: up run down clean

up:
	docker compose up -d
	@echo "Waiting for postgres to be ready..."
	@sleep 3

run:
	python3 rag_pipeline.py

down:
	docker compose down

clean:
	docker compose down -v
	rm -rf .venv __pycache__ *.pyc
