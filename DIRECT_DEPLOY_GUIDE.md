# 🚀 ПРЯМОЕ РАЗВЕРТЫВАНИЕ БЕЗ DOCKER HUB

## Концепция
```
GitHub Actions → SSH → VPS → Git Clone → Docker Build → Docker Run
```

**Никаких внешних registry!** Код клонируется напрямую на VPS и собирается локально.

## 🔧 Настройка VPS

### 1. Подготовка сервера
```bash
# Обновление системы (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo apt install docker-compose-plugin

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# Проверка установки
docker --version
docker compose version
```

### 2. Настройка Git (если нужно для приватных репозиториев)
```bash
# Настройка глобального Git
git config --global user.name "VPS Deploy"
git config --global user.email "deploy@yourdomain.com"

# Для приватных репозиториев (опционально)
ssh-keygen -t rsa -b 4096 -C "vps-deploy-key"
# Добавить публичный ключ в GitHub Deploy Keys
```

## 🔐 Настройка SSH ключей

### 1. Генерация ключей (локально)
```bash
# Создание SSH ключа для CI/CD
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/gitti_deploy

# Копирование публичного ключа на VPS
ssh-copy-id -i ~/.ssh/gitti_deploy.pub user@your-vps-ip
```

### 2. Тестирование подключения
```bash
# Проверка SSH подключения
ssh -i ~/.ssh/gitti_deploy user@your-vps-ip "echo 'SSH подключение работает!'"
```

## ⚙️ GitHub Secrets

Добавьте в репозиторий (Settings → Secrets and variables → Actions):

| Secret Name | Значение | Описание |
|-------------|----------|----------|
| `VPS_HOST` | `123.45.67.89` | IP адрес вашего VPS |
| `VPS_USER` | `ubuntu` или `root` | Пользователь SSH |
| `VPS_SSH_KEY` | `-----BEGIN RSA PRIVATE KEY-----...` | Приватный SSH ключ |
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF...` | Токен Telegram бота |
| `GEMINI_API_KEY` | `AIza...` | API ключ Google Gemini |

### Получение приватного ключа:
```bash
# Показать приватный ключ для копирования в GitHub
cat ~/.ssh/gitti_deploy
```

## 🤖 Получение токенов

### Telegram Bot Token
1. Найти [@BotFather](https://t.me/BotFather) в Telegram
2. Отправить `/newbot`
3. Выбрать имя и username бота
4. Скопировать полученный токен

### Google Gemini API Key
1. Перейти в [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Нажать "Create API key"
3. Скопировать ключ

## 🚀 Процесс развертывания

### Автоматическое развертывание
```bash
# Любой push в main ветку запустит развертывание
git add .
git commit -m "Deploy bot updates"
git push origin main
```

### Ручное развертывание на VPS
```bash
# На VPS сервере
cd ~
git clone https://github.com/your-username/your-repo.git gitti-bot
cd gitti-bot

# Создание конфигурации
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_telegram_token
GEMINI_API_KEY=your_gemini_key
DEBUG=false
LOG_LEVEL=INFO
EOF

# Создание директорий
mkdir -p data/{user_data,logs}

# Сборка и запуск
docker-compose build --no-cache
docker-compose up -d

# Проверка статуса
docker-compose ps
docker-compose logs -f gitti-bot
```

## 📊 Мониторинг

### Полезные команды на VPS
```bash
# Статус контейнеров
docker-compose ps

# Логи в реальном времени
docker-compose logs -f gitti-bot

# Последние 50 строк логов
docker-compose logs --tail=50 gitti-bot

# Использование ресурсов
docker stats gitti-telegram-bot

# Перезапуск бота
docker-compose restart gitti-bot

# Полная пересборка
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Автоматические задачи (cron)
```bash
# Добавить в crontab для автоматической очистки
crontab -e

# Очистка логов каждый день в 2:00
0 2 * * * cd ~/gitti-bot && docker system prune -f

# Перезапуск бота каждую неделю в воскресенье в 3:00
0 3 * * 0 cd ~/gitti-bot && docker-compose restart gitti-bot
```

## 🔍 Отладка проблем

### Типичные ошибки и решения

**1. Ошибка SSH подключения**
```bash
# Проверка SSH ключа
ssh-keygen -l -f ~/.ssh/gitti_deploy

# Проверка прав доступа
chmod 600 ~/.ssh/gitti_deploy
chmod 644 ~/.ssh/gitti_deploy.pub
```

**2. Ошибка Docker сборки**
```bash
# Проверка места на диске
df -h

# Очистка Docker кэша
docker system prune -af --volumes
```

**3. Бот не отвечает**
```bash
# Проверка токенов
docker-compose exec gitti-bot printenv | grep TOKEN

# Проверка сетевого подключения
docker-compose exec gitti-bot ping -c 3 api.telegram.org
```

## 🎯 Преимущества подхода

✅ **Простота**: Никаких external registries  
✅ **Безопасность**: Код собирается на собственном сервере  
✅ **Скорость**: Нет загрузки больших образов  
✅ **Контроль**: Полный контроль над процессом  
✅ **Отладка**: Легко отладить проблемы на сервере  
✅ **Экономия**: Не нужны платные registry сервисы  

## 🔄 Workflow схема

```mermaid
graph TD
    A[Git Push] --> B[GitHub Actions]
    B --> C[SSH to VPS]
    C --> D[Git Clone/Pull]
    D --> E[Create .env]
    E --> F[Docker Build]
    F --> G[Docker Run]
    G --> H[Health Check]
    H --> I[Success ✅]
```

## 📝 Локальная разработка

```bash
# Клонирование проекта
git clone <repository-url>
cd gitti-bot

# Настройка окружения
make setup

# Редактирование .env файла
nano .env

# Запуск для разработки
make dev-run

# Или через Docker
make run
```

## 🆘 Поддержка

При возникновении проблем:

1. **Проверьте логи**: `make logs`
2. **Проверьте статус**: `make status`  
3. **Пересоберите**: `make restart`
4. **Очистите кэш**: `make docker-clean`

---

**Готово!** Теперь у вас есть полностью автономное развертывание без зависимости от внешних registry сервисов! 🎸✨
