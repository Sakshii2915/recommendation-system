.PHONY: help install test run deploy clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make run        - Run FastAPI locally"
	@echo "  make deploy     - Deploy to AWS"
	@echo "  make build      - Build Docker image"
	@echo "  make clean      - Clean build artifacts"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

deploy:
	sam build && sam deploy --guided

build:
	docker build -t recommendation-api .

clean:
	rm -rf __pycache__ .pytest_cache .aws-sam
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

seed:
	python scripts/seed_data.py

lint:
	black app/ lambda_functions/ tests/
	flake8 app/ lambda_functions/ tests/

