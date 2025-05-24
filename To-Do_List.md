# 🌱 PlantCare Agent — To-Do List

> **Критически важно**: Этот список обязателен к строгому исполнению. Переход к следующей задаче разрешен только после полного завершения текущей и отметки `✅`.

---

## 📊 Прогресс проекта
- **Общий прогресс**: 0/38 задач (0%)
- **Текущий этап**: Подготовка
- **Последнее обновление**: [дата]

---

## 🔧 Этап 1: Подготовка и инфраструктура

### 1.1 Окружение разработки
- [x] **ENV-001**: Создать и активировать виртуальное окружение Python 3.11+ ✅ done
- [x] **ENV-002**: Настроить `.gitignore` для Python проекта ✅ done
- [x] **ENV-003**: Инициализировать git репозиторий ✅ done (created instructions + README)

### 1.2 Установка зависимостей
- [x] **DEP-001**: Установить `openai-agents-python>=0.1.0` ✅ done (in requirements.txt)
- [x] **DEP-002**: Установить `python-telegram-bot>=20.0` ✅ done (in requirements.txt)
- [x] **DEP-003**: Установить `Pillow>=10.0.0` ✅ done (in requirements.txt)
- [x] **DEP-004**: Установить `SQLAlchemy>=2.0.0` ✅ done (in requirements.txt)
- [x] **DEP-005**: Установить `python-dotenv>=1.0.0` ✅ done (in requirements.txt)
- [x] **DEP-006**: Установить `pydantic>=2.0.0` ✅ done (in requirements.txt)
- [x] **DEP-007**: Установить `asyncio-mqtt` (для будущих уведомлений) ✅ done (in requirements.txt)
- [x] **DEP-008**: Создать и зафиксировать `requirements.txt` ✅ done

### 1.3 Структура проекта
- [ ] **STRUCT-001**: Создать корневую директорию `PlantMamaAIBot/`
  ```
  PlantMamaAIBot/
  ├── __init__.py
  ├── main.py
  ├── config/
  │   ├── __init__.py
  │   └── settings.py
  ├── core/
  │   ├── __init__.py
  │   └── agent.py
  ├── tools/
  │   ├── __init__.py
  │   ├── plant_diagnosis.py
  │   ├── care_recommendations.py
  │   └── user_management.py
  ├── handlers/
  │   ├── __init__.py
  │   └── telegram_handler.py
  ├── database/
  │   ├── __init__.py
  │   ├── models.py
  │   ├── connection.py
  │   └── migrations/
  ├── services/
  │   ├── __init__.py
  │   ├── image_processing.py
  │   └── plant_knowledge.py
  ├── utils/
  │   ├── __init__.py
  │   ├── logging_config.py
  │   └── validators.py
  └── tests/
      ├── __init__.py
      ├── test_agent.py
      ├── test_tools.py
      └── test_handlers.py
  ```
- [ ] **STRUCT-002**: Создать `.env.example` с шаблоном переменных
- [ ] **STRUCT-003**: Создать `README.md` с описанием проекта

---

## 🤖 Этап 2: Разработка инструментов агента

### 2.1 Диагностика растений
- [ ] **TOOL-001**: `diagnose_plant_photo(image_data: bytes, user_context: Dict) -> DiagnosisResult`
  - Анализ через OpenAI Vision API
  - Детекция болезней, вредителей, дефицитов
  - Оценка общего состояния (1-10)
- [ ] **TOOL-002**: `identify_plant_species(image_data: bytes) -> PlantIdentification`
  - Определение вида растения
  - Confidence score
  - Альтернативные варианты

### 2.2 Рекомендации по уходу
- [ ] **TOOL-003**: `generate_care_instructions(plant_id: str, diagnosis: DiagnosisResult, season: str) -> CareInstructions`
  - Персонализированные советы
  - Учет сезонности и климата
  - Пошаговые инструкции
- [ ] **TOOL-004**: `recommend_fertilizers(plant_type: str, soil_condition: str, season: str) -> List[FertilizerRecommendation]`
  - NPK соотношения
  - Органические vs минеральные
  - Дозировка и частота
- [ ] **TOOL-005**: `recommend_tools(care_task: str, plant_size: str) -> List[ToolRecommendation]`
  - Инструменты для обрезки, пересадки, полива
  - Ценовые категории
  - Ссылки на товары

### 2.3 База знаний растений
- [ ] **TOOL-006**: `get_plant_encyclopedia(plant_name: str) -> PlantInfo`
  - Научная классификация
  - Естественная среда обитания
  - Требования к уходу
- [ ] **TOOL-007**: `calculate_watering_schedule(plant_id: str, pot_size: str, humidity: float) -> WateringSchedule`
  - Частота полива
  - Объем воды
  - Индикаторы для проверки

### 2.4 Пользовательские сессии
- [ ] **TOOL-008**: `save_user_session(user_id: str, session_data: SessionData) -> None`
  - Сохранение в БД
  - Шифрование личных данных
- [ ] **TOOL-009**: `get_user_plant_history(user_id: str) -> List[PlantRecord]`
  - История диагнозов
  - Прогресс лечения
- [ ] **TOOL-010**: `schedule_reminder(user_id: str, reminder_type: str, datetime: datetime) -> None`
  - Напоминания о поливе/подкормке
  - Интеграция с календарем

---

## 📡 Этап 3: Telegram Bot Integration

### 3.1 Базовая настройка
- [ ] **TG-001**: Настроить Telegram Bot через BotFather
- [ ] **TG-002**: Реализовать Webhook с SSL сертификатом
- [ ] **TG-003**: Добавить fallback на Long Polling для разработки

### 3.2 Обработчики сообщений
- [ ] **TG-004**: `/start` — приветствие и регистрация пользователя
- [ ] **TG-005**: `/help` — справка по командам
- [ ] **TG-006**: `/my_plants` — список растений пользователя
- [ ] **TG-007**: Обработка фотографий растений (max 10MB)
- [ ] **TG-008**: Обработка текстовых вопросов о растениях
- [ ] **TG-009**: Обработка голосовых сообщений (через Speech-to-Text)

### 3.3 Интерактивные элементы
- [ ] **TG-010**: Inline клавиатуры для быстрых действий
- [ ] **TG-011**: Callback handlers для кнопок
- [ ] **TG-012**: Пагинация для длинных списков
- [ ] **TG-013**: Progress bars для длительных операций

### 3.4 Уведомления
- [ ] **TG-014**: Система напоминаний о поливе
- [ ] **TG-015**: Уведомления о сезонных работах
- [ ] **TG-016**: Новости и советы (еженедельная рассылка)

---

## 💾 Этап 4: База данных и персистентность

### 4.1 Модели данных
- [ ] **DB-001**: Модель `User` (id, telegram_id, username, preferences, created_at)
- [ ] **DB-002**: Модель `Plant` (id, user_id, name, species, photo_url, added_at)
- [ ] **DB-003**: Модель `Session` (id, user_id, start_time, end_time, messages_count)
- [ ] **DB-004**: Модель `Message` (id, session_id, role, content, timestamp, tokens_used)
- [ ] **DB-005**: Модель `Diagnosis` (id, plant_id, image_url, result, confidence, created_at)
- [ ] **DB-006**: Модель `Reminder` (id, user_id, plant_id, type, scheduled_at, status)

### 4.2 Подключение и миграции
- [ ] **DB-007**: Настроить подключение к PostgreSQL
- [ ] **DB-008**: Создать Alembic миграции
- [ ] **DB-009**: Настроить connection pooling
- [ ] **DB-010**: Добавить индексы для производительности

### 4.3 Repository паттерн
- [ ] **DB-011**: `UserRepository` с методами CRUD
- [ ] **DB-012**: `PlantRepository` с поиском и фильтрацией
- [ ] **DB-013**: `SessionRepository` с агрегацией статистики

---

## 🧠 Этап 5: Основной агент

### 5.1 Конфигурация агента
- [ ] **AGENT-001**: Настроить `Agent` с системным промптом
- [ ] **AGENT-002**: Подключить все разработанные tools
- [ ] **AGENT-003**: Настроить `Runner` с обработкой ошибок
- [ ] **AGENT-004**: Добавить context management для длинных диалогов

### 5.2 Обработка запросов
- [ ] **AGENT-005**: Роутинг между различными типами запросов
- [ ] **AGENT-006**: Обработка мультимодальных входов (текст + фото)
- [ ] **AGENT-007**: Генерация структурированных ответов
- [ ] **AGENT-008**: Интеграция с Telegram handlers

### 5.3 Тестирование сценариев
- [ ] **AGENT-009**: Тест: фото → диагноз → рекомендации → сохранение
- [ ] **AGENT-010**: Тест: вопрос о поливе → персональный совет
- [ ] **AGENT-011**: Тест: планирование ухода на месяц
- [ ] **AGENT-012**: Тест: множественные растения одного пользователя

---

## 🔍 Этап 6: Наблюдаемость и качество

### 6.1 Логгирование
- [ ] **LOG-001**: Настроить structured logging (JSON format)
- [ ] **LOG-002**: Логировать все API вызовы с timing
- [ ] **LOG-003**: Логировать ошибки с full stack trace
- [ ] **LOG-004**: Настроить ротацию логов по размеру и времени
- [ ] **LOG-005**: Добавить correlation ID для трейсинга запросов

### 6.2 Мониторинг
- [ ] **MON-001**: Метрики использования API (tokens, requests/min)
- [ ] **MON-002**: Метрики производительности (response time, queue length)
- [ ] **MON-003**: Метрики ошибок (error rate, error types)
- [ ] **MON-004**: Health check endpoint для мониторинга

### 6.3 Тестирование
- [ ] **TEST-001**: Unit тесты для всех tools (coverage > 80%)
- [ ] **TEST-002**: Integration тесты для Telegram handlers
- [ ] **TEST-003**: End-to-end тесты основных пользовательских сценариев
- [ ] **TEST-004**: Load тесты для concurrent users
- [ ] **TEST-005**: Тесты безопасности (input validation, rate limiting)

---

## 🚀 Этап 7: Деплой и продакшн

### 7.1 Контейнеризация
- [ ] **DEPLOY-001**: Создать оптимизированный Dockerfile
- [ ] **DEPLOY-002**: Настроить docker-compose для локальной разработки
- [ ] **DEPLOY-003**: Создать production docker-compose с PostgreSQL

### 7.2 CI/CD
- [ ] **DEPLOY-004**: Настроить GitHub Actions для тестов
- [ ] **DEPLOY-005**: Автоматический деплой при push в main
- [ ] **DEPLOY-006**: Blue-green deployment strategy

### 7.3 Безопасность
- [ ] **SEC-001**: Rate limiting для API endpoints
- [ ] **SEC-002**: Input validation и sanitization
- [ ] **SEC-003**: Шифрование чувствительных данных в БД
- [ ] **SEC-004**: Audit logging для административных действий

---

## 📏 Стандарты качества

### Код-стиль
- ✅ PEP8 compliance (проверять через `black` и `flake8`)
- ✅ Type hints для всех функций и методов
- ✅ Docstrings в формате Google Style
- ✅ Async/await для всех I/O операций

### Документация
- ✅ README с quick start guide
- ✅ API документация для всех tools
- ✅ Схема архитектуры системы
- ✅ Инструкции по деплою

### Безопасность
- ✅ Все секреты в `.env` файлах
- ✅ Валидация всех входящих данных
- ✅ Обработка всех исключений
- ✅ Логирование подозрительной активности

---

## 🏁 Критерии готовности (Definition of Done)

Задача считается выполненной, когда:
1. ✅ Код написан и соответствует стандартам
2. ✅ Добавлены unit тесты (если применимо)
3. ✅ Обновлена документация
4. ✅ Проведено code review (self-review)
5. ✅ Функциональность протестирована вручную
6. ✅ Логирование добавлено для критических операций
7. ✅ Изменения зафиксированы в git с осмысленным commit message

---

## 📝 Журнал выполнения

| Дата | Задача | Статус | Время | Примечания |
|------|--------|---------|-------|------------|
| | | | | |

**Текущая задача**: [указать текущую задачу]
**Время начала**: [время]
**Ожидаемое завершение**: [время]