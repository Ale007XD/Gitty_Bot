"""
Модели данных для контекста пользователя
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class LearningModule(Enum):
    """Модули обучения"""
    INTRODUCTION = 0  # Знакомство
    FIRST_STEPS = 1   # Первые шаги
    BASIC_CHORDS = 2  # Простейшие аккорды
    FIRST_SONG = 3    # Первая песня

class Achievement(Enum):
    """Достижения ученика"""
    FIRST_MEETING = "first_meeting"
    GUITAR_PARTS_LEARNED = "guitar_parts"
    STRINGS_MEMORIZED = "strings_memorized"
    AM_CHORD_MASTERED = "am_chord"
    E_CHORD_MASTERED = "e_chord"
    FIRST_SONG_PLAYED = "first_song"
    WEEK_STREAK = "week_streak"

@dataclass
class UserProgress:
    """Прогресс обучения пользователя"""
    current_module: LearningModule = LearningModule.INTRODUCTION
    completed_modules: List[LearningModule] = field(default_factory=list)
    achievements: List[Achievement] = field(default_factory=list)
    learned_chords: List[str] = field(default_factory=list)
    session_count: int = 0
    last_session_date: Optional[datetime] = None
    user_name: Optional[str] = None

    def add_achievement(self, achievement: Achievement) -> bool:
        """Добавить достижение, если его еще нет"""
        if achievement not in self.achievements:
            self.achievements.append(achievement)
            return True
        return False

    def complete_module(self, module: LearningModule) -> bool:
        """Завершить модуль"""
        if module not in self.completed_modules:
            self.completed_modules.append(module)
            return True
        return False

    def learn_chord(self, chord: str) -> bool:
        """Изучить новый аккорд"""
        chord_upper = chord.upper()
        if chord_upper not in self.learned_chords:
            self.learned_chords.append(chord_upper)
            return True
        return False

@dataclass
class UserContext:
    """Полный контекст пользователя"""
    user_id: int
    chat_id: int
    progress: UserProgress = field(default_factory=UserProgress)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str):
        """Добавить сообщение в историю"""
        if role not in ["user", "model", "system"]:
            role = "user"  # Защита от некорректных ролей

        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_activity = datetime.now()

        # Ограничиваем историю последними 50 сообщениями
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def get_gemini_history(self) -> List[Dict[str, str]]:
        """Получить историю в формате для Gemini"""
        history = []
        # Берем последние 20 сообщений для контекста
        recent_messages = self.conversation_history[-20:]

        for msg in recent_messages:
            if msg["role"] in ["user", "model"]:
                history.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })
        return history
