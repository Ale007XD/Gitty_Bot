#!/bin/bash
# 🚀 Автоматическая настройка VPS для Gitti Bot

set -e

echo "🚀 НАСТРОЙКА VPS ДЛЯ GITTI BOT"
echo "=============================="
echo ""

# Проверка ОС
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ Linux обнаружен"

    # Определение дистрибутива
    if [ -f /etc/debian_version ]; then
        DISTRO="debian"
        echo "📦 Дистрибутив: Debian/Ubuntu"
    elif [ -f /etc/redhat-release ]; then
        DISTRO="redhat"
        echo "📦 Дистрибутив: RedHat/CentOS"
    else
        echo "⚠️  Неизвестный дистрибутив, продолжаем с Debian командами..."
        DISTRO="debian"
    fi
else
    echo "❌ Этот скрипт предназначен для Linux"
    exit 1
fi

echo ""
echo "🔄 Обновление системы..."
if [ "$DISTRO" = "debian" ]; then
    sudo apt update && sudo apt upgrade -y
else
    sudo yum update -y
fi

echo ""
echo "🐳 Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен"
fi

echo ""
echo "📦 Установка Docker Compose..."
if [ "$DISTRO" = "debian" ]; then
    sudo apt install -y docker-compose-plugin
else
    sudo yum install -y docker-compose-plugin
fi

echo ""
echo "👤 Настройка прав пользователя..."
sudo usermod -aG docker $USER
echo "⚠️  Перезайдите в систему для применения прав Docker"

echo ""
echo "🔧 Установка дополнительных пакетов..."
if [ "$DISTRO" = "debian" ]; then
    sudo apt install -y git curl wget htop nano
else
    sudo yum install -y git curl wget htop nano
fi

echo ""
echo "📁 Создание рабочей директории..."
mkdir -p ~/gitti-bot/{data/user_data,data/logs}
cd ~/gitti-bot

echo ""
echo "🔐 Настройка Git..."
git config --global user.name "VPS Deploy"
git config --global user.email "deploy@gitti-bot.local"

echo ""
echo "🔥 Настройка firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw status | grep -q "Status: active" && echo "UFW уже настроен" || {
        sudo ufw enable
        sudo ufw allow ssh
        sudo ufw allow 80
        sudo ufw allow 443
        echo "✅ UFW настроен"
    }
else
    echo "ℹ️  UFW не установлен, пропускаем настройку firewall"
fi

echo ""
echo "🧹 Создание скрипта очистки..."
cat > ~/gitti-bot/cleanup.sh << 'EOF'
#!/bin/bash
echo "🧹 Очистка Docker ресурсов..."
docker system prune -f --volumes
docker image prune -f
echo "✅ Очистка завершена"
EOF

chmod +x ~/gitti-bot/cleanup.sh

echo ""
echo "📋 Создание скрипта мониторинга..."
cat > ~/gitti-bot/monitor.sh << 'EOF'
#!/bin/bash
echo "📊 Статус Gitti Bot"
echo "=================="
echo ""
echo "🐳 Docker контейнеры:"
docker-compose ps 2>/dev/null || echo "Контейнеры не запущены"
echo ""
echo "💾 Использование диска:"
df -h /
echo ""
echo "🧠 Использование памяти:"
free -h
echo ""
echo "📈 Последние логи:"
docker-compose logs --tail=5 gitti-bot 2>/dev/null || echo "Логи недоступны"
EOF

chmod +x ~/gitti-bot/monitor.sh

echo ""
echo "⏰ Настройка автоматических задач..."
(crontab -l 2>/dev/null; echo "0 2 * * * cd ~/gitti-bot && ./cleanup.sh >/dev/null 2>&1") | crontab -
echo "✅ Автоматическая очистка настроена (ежедневно в 2:00)"

echo ""
echo "🔍 Проверка версий..."
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker compose version)"
echo "Git: $(git --version)"

echo ""
echo "✅ НАСТРОЙКА VPS ЗАВЕРШЕНА!"
echo "=========================="
echo ""
echo "🎯 СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1. 🔑 Настройте SSH ключи для GitHub Actions:"
echo "   ssh-keygen -t rsa -b 4096 -C 'github-actions'"
echo "   cat ~/.ssh/id_rsa.pub"
echo ""
echo "2. 📝 Добавьте GitHub Secrets:"
echo "   VPS_HOST=$(curl -s ifconfig.me)"
echo "   VPS_USER=$USER"  
echo "   VPS_SSH_KEY=<содержимое ~/.ssh/id_rsa>"
echo "   TELEGRAM_BOT_TOKEN=<токен_бота>"
echo "   GEMINI_API_KEY=<ключ_gemini>"
echo ""
echo "3. 🚀 Сделайте git push в репозитории"
echo ""
echo "📊 Полезные команды:"
echo "   ~/gitti-bot/monitor.sh  - мониторинг статуса"
echo "   ~/gitti-bot/cleanup.sh  - очистка ресурсов"
echo ""
echo "🎸 VPS готов для развертывания Gitti Bot! ✨"
