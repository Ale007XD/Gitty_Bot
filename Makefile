# Makefile for Gitti Bot development

.PHONY: help install test lint format clean run docker-build docker-run logs deploy

help:
	@echo "Доступные команды:"
	@echo "  install      - Установить зависимости"
	@echo "  test         - Запустить тесты"
	@echo "  lint         - Проверить код"
	@echo "  format       - Отформатировать код"
	@echo "  clean        - Очистить временные файлы"
	@echo "  run          - Запустить бота локально"
	@echo "  docker-build - Собрать Docker образ"
	@echo "  docker-run   - Запустить через Docker"
	@echo "  logs         - Показать логи"
	@echo "  deploy       - Деплой на продакшн"

install:
	pip install -r app/requirements.txt

test:
	pytest tests/ -v

lint:
	flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

run:
	cd app && python -m bot.main

docker-build:
	docker-compose build

docker-run:
	mkdir -p data/{user_data,logs}
	docker-compose up -d

logs:
	docker-compose logs -f gitti-bot

docker-stop:
	docker-compose down

deploy:
	git push origin main

dev-setup: install
	@echo "🔧 Настройка среды разработки..."
	mkdir -p data/{user_data,logs}
	@if [ ! -f .env ]; then cp .env.example .env; echo "📝 Создан .env файл. Заполните токены!"; fi
	@echo "✅ Готово! Теперь заполните .env файл и запустите 'make run'"

check-env:
	@if [ ! -f .env ]; then echo "❌ Файл .env не найден. Запустите 'make dev-setup'"; exit 1; fi
	@echo "✅ Конфигурация найдена"
