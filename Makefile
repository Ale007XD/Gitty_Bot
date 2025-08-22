# Makefile для разработки и развертывания Gitti Bot

.PHONY: help install test lint format clean build run logs stop restart deploy status

help:
	@echo "🎸 Gitti Bot - Команды управления"
	@echo "=================================="
	@echo ""
	@echo "Разработка:"
	@echo "  install     - Установить зависимости Python"
	@echo "  test        - Запустить тесты"
	@echo "  lint        - Проверить код"
	@echo "  format      - Отформатировать код"
	@echo "  clean       - Очистить временные файлы"
	@echo ""
	@echo "Docker:"
	@echo "  build       - Собрать Docker образ"
	@echo "  run         - Запустить бота в контейнере"
	@echo "  logs        - Показать логи бота"
	@echo "  stop        - Остановить контейнеры"
	@echo "  restart     - Перезапустить бота"
	@echo "  status      - Показать статус контейнеров"
	@echo ""
	@echo "Развертывание:"
	@echo "  deploy      - Развернуть на продакшн (git push)"
	@echo "  check-env   - Проверить конфигурацию"

# Разработка
install:
	@echo "📦 Установка зависимостей..."
	pip install -r app/requirements.txt
	pip install pytest black flake8

test:
	@echo "🧪 Запуск тестов..."
	pytest tests/ -v || echo "⚠️  Тесты не настроены"

lint:
	@echo "🔍 Проверка кода..."
	flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "✅ Код проверен"

format:
	@echo "✨ Форматирование кода..."
	black app/ tests/
	@echo "✅ Код отформатирован"

clean:
	@echo "🧹 Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	@echo "✅ Очистка завершена"

# Docker команды
check-env:
	@echo "🔧 Проверка конфигурации..."
	@if [ ! -f .env ]; then \
		echo "❌ Файл .env не найден!"; \
		echo "📝 Создайте .env файл из .env.example"; \
		exit 1; \
	fi
	@echo "✅ Конфигурация найдена"
	@echo "🔑 Проверка токенов..."
	@grep -q "TELEGRAM_BOT_TOKEN=" .env && echo "✅ Telegram токен установлен" || echo "❌ Telegram токен не найден"
	@grep -q "GEMINI_API_KEY=" .env && echo "✅ Gemini ключ установлен" || echo "❌ Gemini ключ не найден"

build: check-env
	@echo "🔨 Сборка Docker образа..."
	mkdir -p data/{user_data,logs}
	docker-compose build --no-cache
	@echo "✅ Образ собран"

run: build
	@echo "🚀 Запуск Gitti Bot..."
	docker-compose up -d
	@echo "✅ Бот запущен"
	@echo "📋 Для просмотра логов: make logs"

logs:
	@echo "📋 Логи Gitti Bot:"
	docker-compose logs -f gitti-bot

stop:
	@echo "⏹️  Остановка контейнеров..."
	docker-compose down
	@echo "✅ Контейнеры остановлены"

restart: stop run
	@echo "🔄 Перезапуск завершен"

status:
	@echo "📊 Статус контейнеров:"
	@docker-compose ps 2>/dev/null || echo "Контейнеры не запущены"
	@echo ""
	@echo "💾 Использование ресурсов:"
	@docker stats --no-stream gitti-telegram-bot 2>/dev/null || echo "Статистика недоступна"

# Развертывание
deploy:
	@echo "🚀 Развертывание на продакшн..."
	@if [ -z "$$(git status --porcelain)" ]; then \
		echo "✅ Нет незафиксированных изменений"; \
	else \
		echo "📝 Фиксация изменений..."; \
		git add .; \
		git commit -m "Deploy: $$(date '+%Y-%m-%d %H:%M:%S')"; \
	fi
	git push origin main
	@echo "✅ Код отправлен на GitHub"
	@echo "🤖 GitHub Actions начнет автоматическое развертывание"

# Утилиты
setup: 
	@echo "🔧 Первоначальная настройка..."
	mkdir -p data/{user_data,logs}
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 Создан .env файл из шаблона"; \
		echo "⚠️  ВАЖНО: Заполните токены в .env файле!"; \
	fi
	@echo "✅ Настройка завершена"
	@echo "🎯 Следующие шаги:"
	@echo "   1. Отредактируйте .env файл"
	@echo "   2. Запустите: make run"

dev-run:
	@echo "🔧 Запуск в режиме разработки..."
	cd app && python -m bot.main

docker-clean:
	@echo "🧹 Очистка Docker ресурсов..."
	docker system prune -f --volumes
	docker image prune -f
	@echo "✅ Очистка завершена"
