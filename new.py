# Создаем полную структуру проекта для Telegram-бота "Гитти"

import os

# Создаем структуру каталогов
project_structure = {
    'gitti-bot/': {
        '.github/': {
            'workflows/': {
                'deploy.yml': None
            }
        },
        'app/': {
            'bot/': {
                '__init__.py': None,
                'main.py': None,
                'handlers/': {
                    '__init__.py': None,
                    'start.py': None,
                    'learning.py': None
                },
                'services/': {
                    '__init__.py': None,
                    'gemini_service.py': None,
                    'user_service.py': None,
                    'guitar_service.py': None
                },
                'models/': {
                    '__init__.py': None,
                    'user_context.py': None,
                    'learning_progress.py': None
                },
                'utils/': {
                    '__init__.py': None,
                    'image_generator.py': None,
                    'config.py': None
                }
            },
            'requirements.txt': None
        },
        'Dockerfile': None,
        'docker-compose.yml': None,
        'README.md': None,
        '.env.example': None,
        '.gitignore': None
    }
}

def create_structure(structure, base_path=""):
    for item, content in structure.items():
        if item.endswith('/'):
            # Это папка
            folder_path = os.path.join(base_path, item.rstrip('/'))
            os.makedirs(folder_path, exist_ok=True)
            if content:
                create_structure(content, folder_path)
        else:
            # Это файл
            file_path = os.path.join(base_path, item)
            with open(file_path, 'w', encoding='utf-8') as f:
                if content:
                    f.write(content)
                else:
                    f.write("")

# Создаем базовую структуру
create_structure(project_structure)

print("✅ Структура проекта создана успешно!")
print("\n📁 Созданные папки и файлы:")
for root, dirs, files in os.walk("gitti-bot"):
    level = root.replace("gitti-bot", '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        print(f"{subindent}{file}")
