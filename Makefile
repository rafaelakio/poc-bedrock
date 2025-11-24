.PHONY: help install test lint format clean deploy

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make deploy     - Deploy to AWS"
	@echo "  make docker     - Build Docker image"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src tests
	black --check src tests
	isort --check-only src tests
	mypy src --ignore-missing-imports
	bandit -r src -ll

format:
	black src tests
	isort src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf lambda_function.zip
	rm -rf lambda_build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

deploy:
	./scripts/deploy.sh

docker:
	docker build -t bedrock-ocr:latest .

docker-run:
	docker-compose up

setup:
	./scripts/setup_dev.sh

test-local:
	./scripts/test_local.sh
