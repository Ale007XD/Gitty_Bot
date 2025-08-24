# GitHub Secrets Setup Guide

## Обязательные секреты для развертывания

Для корректной работы бота через GitHub Actions необходимо настроить следующие секреты в настройках репозитория.

### 1. Перейдите в настройки секретов
```
GitHub Repository → Settings → Secrets and variables → Actions → Repository secrets
```

### 2. Добавьте следующие секреты:

#### 🤖 TELEGRAM_BOT_TOKEN
- **Описание**: Токен вашего Telegram бота
- **Получение**: @BotFather в Telegram
- **Формат**: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ123456789`
- **Обязательно**: ✅

#### 🤖 GEMINI_API_KEY  
- **Описание**: API ключ Google Gemini
- **Получение**: Google AI Studio (https://makersuite.google.com/app/apikey)
- **Формат**: `AIzaSyC1234567890abcdefghijk_1234567890`
- **Обязательно**: ✅

#### 🌍 GEMINI_REGION (КРИТИЧЕСКИ ВАЖНО!)
- **Описание**: Регион для Gemini API (устраняет ошибку геолокации)
- **Рекомендуемые значения**:
  - `us-central1` (США - наиболее стабильный)
  - `europe-west1` (Европа)
  - `asia-southeast1` (Азия)
- **По умолчанию**: `us-central1`
- **Обязательно**: ✅ (для предотвращения ошибок геолокации)

#### 🖥️ VPS_HOST
- **Описание**: IP адрес или домен вашего VPS
- **Формат**: `123.456.789.123` или `your-domain.com`
- **Обязательно**: ✅

#### 👤 VPS_USER
- **Описание**: Имя пользователя для SSH подключения
- **Формат**: `deploy` или `ubuntu`
- **Обязательно**: ✅

#### 🔑 VPS_SSH_KEY
- **Описание**: Приватный SSH ключ для подключения к VPS
- **Формат**: Полный содержимое файла `~/.ssh/id_rsa`
- **Начинается с**: `-----BEGIN PRIVATE KEY-----`
- **Заканчивается**: `-----END PRIVATE KEY-----`
- **Обязательно**: ✅

## 3. Пример настройки секретов

### В GitHub Repository Secrets добавьте:

```
Name: TELEGRAM_BOT_TOKEN
Value: 1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ123456789

Name: GEMINI_API_KEY  
Value: AIzaSyC1234567890abcdefghijk_1234567890

Name: GEMINI_REGION
Value: us-central1

Name: VPS_HOST
Value: 123.456.789.123

Name: VPS_USER
Value: deploy

Name: VPS_SSH_KEY
Value: -----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...
[остальная часть ключа]
...xyz123==
-----END PRIVATE KEY-----
```

## 4. Проверка настройки

После добавления всех секретов:

1. **Сделайте commit и push в main ветку**
2. **Проверьте GitHub Actions** в разделе Actions
3. **Следите за логами деплоя** для выявления ошибок
4. **Проверьте работу бота** отправив ему сообщение

## 5. Устранение проблем

### Ошибка "User location is not supported"
- ✅ Убедитесь что `GEMINI_REGION` установлен
- ✅ Попробуйте другие регионы: `europe-west1`, `asia-southeast1`
- ✅ Проверьте правильность API ключа Gemini

### Ошибка подключения к VPS
- ✅ Проверьте корректность `VPS_HOST`, `VPS_USER`
- ✅ Убедитесь что SSH ключ скопирован полностью
- ✅ Проверьте что у пользователя есть права Docker

### Ошибка Telegram бота
- ✅ Проверьте корректность `TELEGRAM_BOT_TOKEN`
- ✅ Убедитесь что бот не запущен в другом месте

## 6. Безопасность

- 🔒 Никогда не публикуйте секреты в коде
- 🔒 Регулярно ротируйте API ключи
- 🔒 Используйте отдельного пользователя для деплоя
- 🔒 Ограничьте права SSH ключа