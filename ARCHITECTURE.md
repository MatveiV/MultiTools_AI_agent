# Архитектура AI Agent MultiRole Video Bot

## Содержание
1. [Обзор системы (C4 — System Context)](#c4-system-context)
2. [Контейнеры (C4 — Container)](#c4-container)
3. [Компоненты (C4 — Component)](#c4-component)
4. [Бизнес-процесс обработки сообщения (BPMN)](#bpmn-обработка-сообщения)
5. [Бизнес-процесс первичной настройки (BPMN)](#bpmn-первичная-настройка)
6. [Диаграмма классов (UML)](#uml-диаграмма-классов)
7. [Диаграмма последовательности — чат (UML)](#uml-последовательность-чат)
8. [Диаграмма последовательности — генерация изображения (UML)](#uml-последовательность-изображение)
9. [Диаграмма состояний (UML)](#uml-диаграмма-состояний)

---

## C4 — System Context

Уровень 1: система в контексте внешних участников.

```mermaid
C4Context
    title System Context — AI Agent MultiRole Video Bot

    Person(user, "Пользователь", "Отправляет сообщения, выбирает режимы и провайдеров через Telegram")

    System(bot, "AI Agent Bot", "Telegram-бот с поддержкой нескольких AI-провайдеров, памятью диалога, генерацией изображений и видео")

    System_Ext(telegram, "Telegram API", "Доставка сообщений, inline-кнопки, отправка медиафайлов")
    System_Ext(zai, "Z.AI API", "GLM-модели, CogVideoX, GLM-Image")
    System_Ext(proxyapi, "ProxyAPI", "OpenAI GPT-модели, DALL·E, Sora через российский прокси")
    System_Ext(genapi, "GenAPI", "Агрегатор: GPT, Claude, Gemini, DeepSeek, Kling, LTX и др.")
    System_Ext(cerebras, "Cerebras", "Сверхбыстрый инференс Llama, Qwen, GPT OSS")
    System_Ext(huggingface, "HuggingFace Router", "Роутер 18+ провайдеров: Groq, Together, Novita и др.")
    System_Ext(cbr, "ЦБ РФ API", "Курс USD/RUB для расчёта стоимости запросов")

    Rel(user, telegram, "Отправляет сообщения")
    Rel(telegram, bot, "Webhook / Long Polling")
    Rel(bot, telegram, "Ответы, медиафайлы, inline-кнопки")
    Rel(bot, zai, "Chat completions, image/video generation")
    Rel(bot, proxyapi, "Chat completions, image/video generation")
    Rel(bot, genapi, "Chat completions, image/video generation")
    Rel(bot, cerebras, "Chat completions")
    Rel(bot, huggingface, "Chat completions, text-to-image")
    Rel(bot, cbr, "Получение курса валют")
```

---

## C4 — Container

Уровень 2: внутренние контейнеры системы.

```mermaid
C4Container
    title Container Diagram — AI Agent MultiRole Video Bot

    Person(user, "Пользователь")

    System_Ext(telegram, "Telegram API")
    System_Ext(ai_providers, "AI Провайдеры", "Z.AI, ProxyAPI, GenAPI, Cerebras, HuggingFace")
    System_Ext(cbr, "ЦБ РФ API")

    Container_Boundary(bot_system, "AI Agent Bot") {
        Container(main, "main.py", "Python / aiogram 3", "Точка входа. FSM, обработчики команд и сообщений, роутинг запросов к провайдерам")
        Container(config, "config.py", "Python", "Конфигурация провайдеров, моделей, цен токенов. Загрузка из .env")
        Container(memory, "memory.py", "Python", "In-memory кэш + персистентность в JSON. История диалогов и настройки пользователей")
        ContainerDb(memory_json, "memory.json", "JSON файл", "История диалогов всех пользователей")
        ContainerDb(settings_json, "user_settings.json", "JSON файл", "Настройки провайдера, модели, температуры, режима")
        ContainerDb(prompts_json, "prompts.json", "JSON файл", "Системные промпты для ролей (assistant, developer, architect и др.)")
        ContainerDb(log_file, "bot.log", "Log файл", "Ротируемый лог (5MB × 3 файла)")
    }

    Rel(user, telegram, "Telegram messages")
    Rel(telegram, main, "Updates via Long Polling")
    Rel(main, telegram, "sendMessage, sendDocument, sendVideo")
    Rel(main, config, "Читает провайдеров и модели")
    Rel(main, memory, "Читает/пишет историю и настройки")
    Rel(memory, memory_json, "Персистентность")
    Rel(memory, settings_json, "Персистентность")
    Rel(main, prompts_json, "Загружает роли при старте")
    Rel(main, ai_providers, "OpenAI-совместимые запросы / нативные API")
    Rel(main, cbr, "GET курс USD/RUB")
    Rel(main, log_file, "Запись логов")
```

---

## C4 — Component

Уровень 3: компоненты внутри `main.py`.

```mermaid
C4Component
    title Component Diagram — main.py

    Container_Boundary(main, "main.py") {
        Component(cmd_handlers, "Command Handlers", "aiogram handlers", "/start, /help, /reset, /mode, /settings, /image, /video")
        Component(fsm_setup, "FSM Setup", "aiogram FSM", "Состояния выбора провайдера → модели → температуры")
        Component(fsm_video, "FSM VideoGen", "aiogram FSM", "Состояние ожидания промпта для генерации видео")
        Component(fsm_image, "FSM ImageGen", "aiogram FSM", "Состояние ожидания промпта для генерации изображения")
        Component(msg_handler, "Message Handler", "aiogram handler", "Основной обработчик текстовых сообщений → AI запрос")
        Component(keyboards, "Keyboard Builders", "Python functions", "Построение inline-клавиатур: провайдеры, модели, температуры, режимы")
        Component(cost_calc, "Cost Calculator", "async function", "Подсчёт стоимости запроса в USD и RUB по курсу ЦБ РФ")
        Component(genapi_poll, "_genapi_generate", "async function", "Нативный GenAPI: POST /networks/{id} → polling /request/get/{id}")
        Component(openai_client, "_make_openai_client", "function", "Создание AsyncOpenAI клиента для провайдера")
        Component(chunker, "Message Chunker", "inline logic", "Разбивка ответов >4000 символов на части")
    }

    Rel(cmd_handlers, fsm_setup, "Запускает FSM настройки")
    Rel(cmd_handlers, fsm_video, "Запускает FSM видео")
    Rel(cmd_handlers, fsm_image, "Запускает FSM изображения")
    Rel(fsm_setup, keyboards, "Использует клавиатуры")
    Rel(msg_handler, openai_client, "Создаёт клиент")
    Rel(msg_handler, cost_calc, "Считает стоимость")
    Rel(msg_handler, chunker, "Разбивает длинные ответы")
    Rel(fsm_image, genapi_poll, "Для GenAPI провайдера")
    Rel(fsm_video, genapi_poll, "Для GenAPI провайдера")
```

---

## BPMN — Обработка сообщения

Бизнес-процесс обработки входящего текстового сообщения пользователя.

```mermaid
flowchart TD
    Start([Пользователь отправил сообщение]) --> CheckConfig{Настроен\nпровайдер?}
    CheckConfig -- Нет --> AskSetup[Предложить /start]
    CheckConfig -- Да --> LoadSettings[Загрузить настройки\nпровайдер, модель, температура, режим]
    LoadSettings --> LoadHistory[Загрузить историю\nдиалога из памяти]
    LoadHistory --> BuildContext[Сформировать контекст:\nsystem_prompt + история + новое сообщение]
    BuildContext --> SendTyping[Отправить typing action]
    SendTyping --> CallAI[Запрос к AI провайдеру\nOpenAI-совместимый API]
    CallAI --> APIError{Ошибка\nAPI?}
    APIError -- Да --> CheckGeoBlock{Блокировка\nпо региону?}
    CheckGeoBlock -- Да --> NotifyGeo[Сообщить о блокировке\nпредложить другой провайдер]
    CheckGeoBlock -- Нет --> NotifyError[Показать ошибку\nс командами]
    APIError -- Нет --> SaveHistory[Сохранить user+assistant\nв память]
    SaveHistory --> GetRate[Получить курс USD/RUB\nот ЦБ РФ]
    GetRate --> CalcCost[Рассчитать стоимость\nтокенов в ₽]
    CalcCost --> CheckLength{Ответ > 4000\nсимволов?}
    CheckLength -- Да --> SplitChunks[Разбить на части\nпо 4000 символов]
    SplitChunks --> SendChunks[Отправить каждую часть\nс командами в последней]
    CheckLength -- Нет --> SendReply[Отправить ответ\n+ стоимость + команды]
    SendReply --> End([Завершено])
    SendChunks --> End
    NotifyGeo --> End
    NotifyError --> End
    AskSetup --> End
```

---

## BPMN — Первичная настройка

Процесс первичной настройки бота пользователем через FSM.

```mermaid
flowchart TD
    Start([/start или /settings]) --> ShowProviders[Показать список\nпровайдеров с кнопками]
    ShowProviders --> SelectProvider[Пользователь выбирает\nпровайдера]
    SelectProvider --> ShowModels[Показать модели\nпровайдера с описаниями]
    ShowModels --> SelectModel[Пользователь выбирает\nмодель]
    SelectModel --> ShowTemps[Показать варианты\nтемпературы]
    ShowTemps --> SelectTemp[Пользователь выбирает\nтемпературу]
    SelectTemp --> SaveSettings[Сохранить настройки\nв user_settings.json]
    SaveSettings --> SetDefaultMode[Установить режим\nпо умолчанию: assistant]
    SetDefaultMode --> Confirm[Показать подтверждение\nс итоговыми настройками]
    Confirm --> ChangeMode{Сменить\nрежим?}
    ChangeMode -- Да --> ShowModes[Команда mode —\nпоказать список ролей]
    ShowModes --> SelectMode[Выбрать роль]
    SelectMode --> ClearHistory[Очистить историю\nдиалога]
    ClearHistory --> End([Готов к работе])
    ChangeMode -- Нет --> End
```

---

## UML — Диаграмма классов

```mermaid
classDiagram
    class Config {
        +BOT_TOKEN: str
        +PROVIDERS: dict
        +MAX_HISTORY_MESSAGES: int
        +MEMORY_FILE: str
        +SETTINGS_FILE: str
        +PROMPTS_FILE: str
        +CBR_API_URL: str
        +TOKEN_PRICES_USD_PER_1M: dict
    }

    class MemoryModule {
        -_history: dict~int, list~
        -_settings: dict~int, dict~
        +load_all() None
        +save_all() None
        +get_history(chat_id) list
        +add_message(chat_id, role, content) None
        +reset_history(chat_id) None
        +get_settings(chat_id) dict
        +save_settings(chat_id, settings) None
        +get_setting(chat_id, key, default) Any
        +update_setting(chat_id, key, value) None
    }

    class Provider {
        +name: str
        +api_key_env: str
        +api_key: str
        +base_url: str
        +models: dict
        +image_models: dict
        +video_models: dict
    }

    class Model {
        +id: str
        +label: str
        +free: bool
        +temp_range: tuple
        +max_tokens: int
        +desc: str
    }

    class MediaModel {
        +id: str
        +label: str
        +desc: str
        +price: str
    }

    class FSMSetup {
        +choose_provider: State
        +choose_model: State
        +choose_temperature: State
    }

    class FSMVideoGen {
        +waiting_prompt: State
    }

    class FSMImageGen {
        +waiting_prompt: State
    }

    class BotHandlers {
        +cmd_start(message, state) None
        +cmd_help(message) None
        +cmd_reset(message) None
        +cmd_mode(message) None
        +cmd_settings(message, state) None
        +cmd_video(message, state) None
        +cmd_image(message, state) None
        +handle_message(message) None
        +handle_video_prompt(message, state) None
        +handle_image_prompt(message, state) None
    }

    class CostCalculator {
        +get_usd_rate() float
        +calc_cost_rub(model_id, prompt_tokens, completion_tokens) str
    }

    Config "1" --> "*" Provider : содержит
    Provider "1" --> "*" Model : содержит
    Provider "1" --> "*" MediaModel : содержит
    BotHandlers --> MemoryModule : использует
    BotHandlers --> Config : читает
    BotHandlers --> CostCalculator : вызывает
    BotHandlers --> FSMSetup : управляет
    BotHandlers --> FSMVideoGen : управляет
    BotHandlers --> FSMImageGen : управляет
```

---

## UML — Последовательность: чат

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant TG as Telegram API
    participant Bot as main.py
    participant Mem as memory.py
    participant AI as AI Провайдер
    participant CBR as ЦБ РФ API

    User->>TG: Отправляет текстовое сообщение
    TG->>Bot: Update (message)
    Bot->>Mem: get_settings(chat_id)
    Mem-->>Bot: {provider, model, temperature, mode}
    Bot->>Mem: get_history(chat_id)
    Mem-->>Bot: [список сообщений]
    Bot->>TG: sendChatAction(typing)
    Bot->>AI: POST /chat/completions\n{model, messages, temperature, max_tokens}
    AI-->>Bot: {choices[0].message, usage}
    Bot->>Mem: add_message(user), add_message(assistant)
    Bot->>CBR: GET /daily_json.js
    CBR-->>Bot: {USD.Value: 81.30}
    Bot->>Bot: calc_cost_rub(tokens, rate)
    alt Ответ > 4000 символов
        loop Каждый чанк
            Bot->>TG: sendMessage(chunk)
        end
    else Ответ ≤ 4000 символов
        Bot->>TG: sendMessage(reply + cost + commands)
    end
    TG-->>User: Ответ бота
```

---

## UML — Последовательность: генерация изображения

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant TG as Telegram API
    participant Bot as main.py
    participant GenAPI as GenAPI\n(нативный API)
    participant OtherAI as ProxyAPI / Z.AI / HF\n(OpenAI-совместимый)

    User->>TG: /image
    TG->>Bot: Update (/image)
    Bot->>TG: Клавиатура выбора модели\n(с провайдером и ценой)
    User->>TG: Выбирает модель
    TG->>Bot: callback_data=imgmodel:p_key:m_key
    Bot->>TG: "Опиши изображение..."
    User->>TG: Текстовый промпт
    TG->>Bot: Update (message в FSM ImageGen)
    Bot->>TG: "⏳ Генерирую изображение..."

    alt GenAPI (p_key=3)
        Bot->>GenAPI: POST /api/v1/networks/{model_id}\n{prompt}
        GenAPI-->>Bot: {request_id, status: processing}
        loop Polling каждые 5 сек
            Bot->>GenAPI: GET /api/v1/request/get/{id}
            GenAPI-->>Bot: {status, result: [url]}
        end
        Bot->>GenAPI: GET image_url
        GenAPI-->>Bot: bytes
    else HuggingFace (p_key=6)
        Bot->>OtherAI: InferenceClient.text_to_image(prompt, model)
        OtherAI-->>Bot: PIL Image
        Bot->>Bot: PIL → PNG bytes
    else ProxyAPI / Z.AI (p_key=1,2)
        Bot->>OtherAI: POST /images/generations\n{model, prompt, response_format: b64_json}
        OtherAI-->>Bot: {data[0].b64_json}
        Bot->>Bot: base64 decode → bytes
    end

    Bot->>TG: sendDocument(image.png + caption)
    Bot->>TG: sendMessage(команды)
    TG-->>User: Изображение + команды
```

---

## UML — Диаграмма состояний

FSM-состояния бота для одного пользователя.

```mermaid
stateDiagram-v2
    [*] --> Idle : Бот запущен

    Idle --> SetupProvider : /start или /settings
    SetupProvider --> SetupModel : Выбран провайдер
    SetupModel --> SetupTemperature : Выбрана модель
    SetupTemperature --> Idle : Выбрана температура\n(настройки сохранены)

    Idle --> ModeSelection : /mode
    ModeSelection --> Idle : Выбран режим\n(история очищена)

    Idle --> VideoPrompt : /video → выбрана модель
    VideoPrompt --> Idle : Промпт отправлен\n(видео генерируется)

    Idle --> ImagePrompt : /image → выбрана модель
    ImagePrompt --> Idle : Промпт отправлен\n(изображение генерируется)

    Idle --> Idle : Текстовое сообщение\n(AI ответ + стоимость)
    Idle --> Idle : /reset\n(история очищена)
    Idle --> Idle : /help

    note right of Idle
        Основное рабочее состояние.
        Принимает текстовые сообщения
        и команды.
    end note

    note right of SetupProvider
        FSM: Setup
        Inline-кнопки провайдеров
    end note

    note right of VideoPrompt
        FSM: VideoGen
        Ожидает текстовый промпт
    end note
```
