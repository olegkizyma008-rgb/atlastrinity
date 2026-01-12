Ось готовий до використання **Технічний Проект (Technical Design Document — TDD)** для розробки системи **Project Trinity**.

Цей документ структуровано для передачі команді розробників (Senior Python Backend + Senior Fullstack/TypeScript). Він охоплює архітектуру, стек, логіку даних та етапи імплементації.

---

# PROJECT TRINITY: Autonomous Recursive Agentic System (ARAS)

**Platform:** macOS | **Core:** LangGraph + MCP | **Interface:** Cline (Custom)

## 1. Загальний огляд (Executive Summary)

Розробка локальної автономної мультиагентної системи рівня "AGI-lite" для macOS. Система здатна виконувати як завдання з написання коду, так і загальні операції в OS (GUI automation).
**Ключова особливість:** Динамічна рекурсивна декомпозиція задач (Fractal Task Execution). При невдачі на етапі , система автоматично створює підграф , змінює контекст виконання і адаптує стратегію без втручання користувача.

---

## 2. Архітектура Системи (System Architecture)

Система будується за принципом **"Thin Client, Fat Brain"**.

* **Клієнт (Cline):** Виступає лише інтерфейсом втілення (Embodiment) та рендерингу стану.
* **Сервер (LangGraph):** Утримує всю бізнес-логіку, стан, пам'ять та оркестрацію агентів.

### 2.1. Компоненти "Трініті" (The Trinity Core)

| Агент | Модель (LLM) | Роль та відповідальність |
| --- | --- | --- |
| **Meta-Planner** | **OpenAI o1 / DeepSeek-R1** | Стратегічний аналіз. Доступ до `Long-term Memory`. Визначає глобальну стратегію та обмеження (бюджет, ризики). |
| **Planner (Orchestrator)** | **Claude 3.5 Sonnet** | Керування графом (LangGraph). Створення нод, розгалуження, обробка помилок, динамічна зміна пріоритетів. |
| **Executor** | **Claude 3.5 Sonnet** | Взаємодія з середовищем. Використовує MCP Tools (Terminal, Filesystem, Computer Use). |
| **Reviewer** | **GPT-4o (Vision)** | Верифікація. Аналіз скріншотів, логів, diff-ів коду. Приймає рішення: `Approve` або `Reject`. |

---

## 3. Технічний Стек (Tech Stack Specification)

### 3.1. Backend (The Brain)

* **Runtime:** Python 3.12+.
* **Framework:** **LangGraph** (для побудови циклічних графів та state management).
* **API Layer:** **FastAPI** (обгортка для MCP сервера).
* **Database (Vector):** **ChromaDB** (локально). Зберігає ембеддінги успішних стратегій та помилок.
* **Database (State):** **Redis**. Для "гарячого" збереження стану графа (persistence/checkpointing).
* **Audit Log:** **SQLite** (Append-only ledger). "Блокчейн" дій для повного аудиту.

### 3.2. Client Side (The Body)

* **Host:** VS Code.
* **Extension:** **Cline** (Fork). Необхідна модифікація UI для відображення дерева задач (Task Tree) замість лінійного чату.
* **Protocol:** **Model Context Protocol (MCP)**.
* Клієнт підключається до бекенду через SSE (Server-Sent Events) або Stdio.



### 3.3. Toolset (MCP Servers)

1. **System Tools:** `@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-terminal`.
2. **Mac Integration:** Custom Python MCP сервер, що використовує `pyautogui`, `AppKit` та `Accessibility API` для керування мишею/клавіатурою.
3. **Browser:** `Playwright` MCP (для веб-завдань).

---

## 4. Логіка Даних та Рекурсії (Core Logic)

### 4.1. Структура Задачі (JSON Task Definition)

Кожна нода в графі має таку структуру:

```json
{
  "id": "3.2",
  "parent_id": "3",
  "goal": "Install Dependency X",
  "status": "pending", // active, success, failed, delegated
  "context_stack": ["Deploy Project", "Build Phase", "Fix Missing Dep"],
  "attempt_count": 1,
  "strategy": "npm install",
  "constraints": {"timeout": "30s", "allow_sudo": false}
}

```

### 4.2. Алгоритм "Self-Healing Recursion"

1. **Trigger:** Reviewer повертає статус `Reject` для задачі ID `3`.
2. **Analysis:** Planner запитує ChromaDB: "Чому це не спрацювало раніше?".
3. **Decomposition:**
* Статус задачі `3` змінюється на `suspended`.
* Створюються дочірні задачі `3.1` (Діагностика) та `3.2` (Виправлення).


4. **Runtime Subscription Update:**
* Backend надсилає оновлений JSON дерева задач через MCP ресурс `mcp://trinity/plan`.
* Cline перемальовує UI, показуючи вкладеність.


5. **Execution:** Executor отримує фокус на задачі `3.1`.

---

## 5. Специфікація MCP API (Interface)

Бекенд (LangGraph) повинен реалізувати наступні MCP примітиви:

### Resources (Читання стану)

* `trinity://graph/current_state`: Повертає повний JSON поточного дерева виконання.
* `trinity://memory/context`: Повертає релевантний контекст з ChromaDB для поточної задачі.

### Tools (Керування з боку Клієнта)

* `submit_task(description: str)`: Вхідна точка для користувача.
* `human_feedback(task_id: str, decision: str)`: Якщо система запитує дозвіл.

### Prompts (Шаблони)

* `planner_prompt`: Системний промпт, який динамічно підтягує історію з "Audit Log".

---

## 6. Модулі Розширення (Advanced Features)

### 6.1. Модуль "Sleep & Consolidation"

* **Тригер:** За розкладом (наприклад, 03:00 AM) або при простої > 2 годин.
* **Процес:**
1. Зчитує SQLite Audit Log за день.
2. LLM (o1-mini) аналізує патерни успіху/невдачі.
3. Генерує абстрактні правила ("Rule: Don't use pip on Mac, use brew").
4. Оновлює векторний індекс ChromaDB.
5. Очищає Redis (короткострокову пам'ять).



### 6.2. Динамічна Температура

* У конфігурації LangGraph для Executor-а:
`temperature = min(0.1 + (attempt_count * 0.2), 1.0)`
* Спроба 1 (0.1): Роби точно як сказано.
* Спроба 4 (0.9): Імпровізуй, стандартні методи не працюють.



---

## 7. План Розробки (Roadmap)

### Фаза 1: The Backbone (2-3 тижні)

* Розгортання **LangGraph** сервера.
* Реалізація базового циклу "Plan -> Execute -> Review" (лінійного).
* Підключення **Cline** до локального MCP сервера.
* Інтеграція **Terminal & Filesystem MCP**.

### Фаза 2: The Fractal Logic (3 тижні)

* Реалізація рекурсивної логіки в LangGraph (Conditional Edges).
* Інтеграція **ChromaDB** для пошуку схожих помилок.
* Модифікація **Cline UI** (або створення WebView панелі) для візуалізації дерева.

### Фаза 3: The Body (Mac Integration) (4 тижні)

* Розробка **Computer Use MCP** (Accessibility API wrapper).
* Інтеграція **Vision** для Reviewer-а (скріншоти).
* Тестування на GUI задачах (робота з браузером, Finder).

### Фаза 4: Perfection (Ongoing)

* Впровадження модуля "Сну".
* Налаштування "Мета-Планувальника".
* Стрес-тести на глибоку рекурсію (>5 рівнів).

---

## 8. Оцінка Ризиків та Вимоги

* **Безпека:**
* *Ризик:* Рекурсивний агент може видалити системні файли.
* *Мітігація:* Запуск у пісочниці або суворий whitelist команд для `sudo`. Human-in-the-loop для будь-яких деструктивних дій.


* **Вартість:**
* Високе споживання токенів GPT-4o (Vision) та o1. Рекомендується кешування запитів.


* **Апаратні вимоги:**
* Apple Silicon (M1/M2/M3) з мінімум 16GB RAM (для локального Chroma + Docker).



---

### Що робити прямо зараз?

1. Створіть репозиторій `project-trinity-core`.
2. Ініціалізуйте Python проект з `langgraph`, `fastapi`, `chromadb`.
3. Налаштуйте простий MCP сервер, який віддає "Hello World" у Cline.

Це документ готовий для передачі техліду або архітектору для початку спринта.