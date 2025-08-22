# Гитти 🎸 - Telegram-бот для обучения игре на гитаре

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![aiogram](https://img.shields.io/badge/aiogram-3.13.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Гитти** - это интерактивный Telegram-бот, который поможет детям 7-12 лет изучить основы игры на гитаре в игровой форме. Бот использует AI-технологии (Google Gemini) для персонализированного обучения и поддерживает геймификацию процесса.

## 🌟 Особенности

### 🎯 Обучающие модули
- **Модуль 0**: Знакомство с инструментом
- **Модуль 1**: Правильная посадка и название струн  
- **Модуль 2**: Первые аккорды (Am, E, G, C, D)
- **Модуль 3**: Первая песня "В траве сидел кузнечик"

### 🎮 Геймификация
- Система достижений (7 типов ачивок)
- Прогрессивное обучение
- Персонализированная обратная связь
- Текстовые диаграммы аккордов

### 🤖 AI-возможности
- Интеллектуальные ответы через Google Gemini
- Память о прогрессе каждого ученика
- Персонализированные советы
- Адаптивная сложность обучения

## 🚀 Быстрый старт

### 1. Получение ключей

#### Telegram Bot Token
1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot` 
3. Выберите имя и username для бота
4. Сохраните полученный токен

#### Google Gemini API Key  
1. Перейдите в [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Нажмите "Create API Key"
3. Сохраните полученный ключ

### 2. Локальный запуск

```bash
# Клонируем репозиторий
git clone <repository-url>
cd gitti-bot

# Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или  
venv\Scripts\activate    # Windows

# Устанавливаем зависимости
pip install -r app/requirements.txt

# Настраиваем конфигурацию
cp .env.example .env
# Отредактируйте .env файл, добавив ваши токены

# Запускаем бота
cd app
python -m bot.main
```

### 3. Запуск через Docker

```bash
# Настройка конфигурации
cp .env.example .env
# Отредактируйте .env файл

# Создание папок для данных  
mkdir -p data/{user_data,logs}

# Запуск через docker-compose
docker-compose up -d

# Проверка статуса
docker-compose logs -f gitti-bot
```

## 🔧 Настройка для продакшена

### GitHub Secrets
В настройках репозитория добавьте:

- `TELEGRAM_BOT_TOKEN` - токен вашего бота
- `GEMINI_API_KEY` - ключ Google Gemini API  
- `VPS_HOST` - IP адрес VPS
- `VPS_USER` - имя пользователя SSH
- `VPS_SSH_KEY` - приватный SSH ключ

### Автоматический деплой
После настройки secrets каждый push в `main` автоматически:
- Соберет Docker образ
- Запушит в GitHub Container Registry
- Развернет на VPS
- Выполнит health check

## 🎸 Команды бота

- `/start` - Начать обучение
- `/progress` - Показать прогресс
- `/chords` - Список аккордов
- `/song` - Текст первой песни
- `/exercises` - Упражнения
- `/achievements` - Достижения
- `/parts` - Части гитары
- `/strings` - Названия струн  
- `/posture` - Правильная посадка
- `/help` - Справка

## 📁 Структура проекта

```
gitti-bot/
├── .github/workflows/    # GitHub Actions
├── app/                  # Исходный код
│   ├── bot/             # Основной код бота
│   │   ├── handlers/    # Обработчики сообщений
│   │   ├── services/    # Сервисы и бизнес-логика
│   │   ├── models/      # Модели данных
│   │   └── utils/       # Утилиты и конфигурация
│   └── requirements.txt # Зависимости
├── data/                # Данные (создается автоматически)
├── tests/              # Тесты
├── Dockerfile          # Docker конфигурация
├── docker-compose.yml  # Оркестрация
└── README.md          # Этот файл
```

## 🤝 Разработка

### Установка для разработки
```bash
pip install -r app/requirements.txt
```

### Запуск тестов  
```bash
pytest tests/ -v
```

### Форматирование кода
```bash
black app/
```

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 🎯 Roadmap

- [ ] Добавление новых аккордов  
- [ ] Система уровней сложности
- [ ] Интеграция с метрономом
- [ ] Веб-интерфейс для родителей
- [ ] Мультиязычная поддержка

---

**Сделано с ❤️ для юных гитаристов** 🎸✨
