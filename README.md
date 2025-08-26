# HR Payroll System 💰

Автоматизированная система создания платежных листов из Google Sheets с выгрузкой в Google Drive.

## 🎯 Основные возможности

- 📥 **Автоматическая загрузка данных** из Google Sheets
- 📄 **Генерация красивых PDF платежных листов** для каждого сотрудника
- ☁️ **Автоматическая выгрузка** в Google Drive с организацией по датам
- 🔄 **Жадная обработка** - создали лист, сразу выгрузили
- 📊 **Учет обработанных записей** в JSON формате
- 🚫 **Предотвращение дублирования** - повторно не создаем уже обработанные листы
- 🔄 **Принудительное пересоздание** при необходимости
- 🌐 **Удобный веб-интерфейс** на Streamlit
- 🔐 **Простая авторизация** (admin/admin)

## 📋 Требования

- Python 3.8+
- Google Service Account с доступом к Google Sheets и Drive API
- Все зависимости из `requirements.txt`

## 🚀 Установка и настройка

### 1. Клонирование и установка зависимостей

```bash
# Переход в директорию проекта
cd hrproject

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка Google API

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API и Google Drive API
3. Создайте Service Account и скачайте JSON файл с ключами
4. Поместите JSON файл в корень проекта (например, `takefinace-1648e5de7102.json`)
5. Предоставьте Service Account доступ к вашим Google Sheets и Drive папкам

### 3. Настройка переменных окружения

Отредактируйте файл `.env`:

```env
GOOGLE_CREDENTIALS_FILE=takefinace-1648e5de7102.json
GOOGLE_FILE_ID=your_google_sheets_file_id
GOOGLE_FOLDER=your_google_drive_folder_id
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORGANIZATION_KEY=your_openai_org_key
```

### 4. Структура данных в Google Sheets

Таблица должна содержать следующие колонки:
- `Location` - Локация сотрудника
- `ID` - Уникальный идентификатор сотрудника
- `Name` - ФИО сотрудника
- `Base` - Базовая информация
- `% from the base` - Процент от базы
- `Payment` - Информация о платеже
- `Base Jan-Mar` - Базовая зарплата за период
- `Bonus USD` - Бонус в долларах
- `SLA` - Показатель выполнения SLA
- `Bonus USD fin` - Финальный бонус в долларах
- `Bonus loc cur` - Бонус в локальной валюте

## 🖥️ Запуск приложения

### Веб-интерфейс (рекомендуется)

```bash
streamlit run streamlit_app.py
```

Откройте браузер и перейдите по адресу `http://localhost:8501`

**Данные для входа:**
- Логин: `admin`
- Пароль: `admin`

### Командная строка

```bash
python payroll_processor.py
```

## 📖 Использование

### Через веб-интерфейс

1. **Авторизация**: Войдите используя admin/admin
2. **Обработка**: 
   - Перейдите в раздел "⚙️ Обработка"
   - Укажите Google Sheets File ID и Google Drive Folder ID
   - При необходимости включите "Принудительное пересоздание"
   - Нажмите "Запустить обработку"
3. **Мониторинг**: Следите за прогрессом в реальном времени
4. **Статистика**: Проверьте результаты в разделе "📊 Статистика"

### Программный интерфейс

```python
from payroll_processor import PayrollProcessor

# Создание процессора
processor = PayrollProcessor()

# Запуск обработки
results = processor.process_payrolls(
    google_file_id="your_sheets_id",
    google_folder_id="your_drive_folder_id",
    force_recreate=False  # True для принудительного пересоздания
)

# Просмотр результатов
print(f"Обработано: {len(results['processed'])}")
print(f"Ошибок: {len(results['failed'])}")
```

## 📁 Структура проекта

```
hrproject/
├── streamlit_app.py           # Веб-интерфейс Streamlit
├── payroll_processor.py       # Основной процессор
├── google_sheets_handler.py   # Работа с Google Sheets
├── pdf_generator.py          # Генерация PDF
├── google_drive_handler.py   # Работа с Google Drive
├── processing_tracker.py     # Отслеживание статусов
├── requirements.txt          # Зависимости Python
├── .env                     # Переменные окружения
├── takefinace-1648e5de7102.json  # Google Service Account ключи
├── processing_status.json   # Статусы обработки (создается автоматически)
├── metadata.md             # Описание методологии расчетов
├── data.md                # Пример структуры данных
└── README.md              # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения (.env)

- `GOOGLE_CREDENTIALS_FILE` - Путь к JSON файлу с ключами Service Account
- `GOOGLE_FILE_ID` - ID Google Sheets файла с данными сотрудников
- `GOOGLE_FOLDER` - ID папки Google Drive для сохранения PDF
- `OPENAI_API_KEY` - API ключ OpenAI (опционально)
- `OPENAI_ORGANIZATION_KEY` - Ключ организации OpenAI (опционально)

### Настройка PDF

Вы можете настроить внешний вид PDF, отредактировав `pdf_generator.py`:
- Стили текста
- Цвета и шрифты
- Структуру документа
- Логотипы и изображения

## 📊 Отслеживание статусов

Система автоматически ведет учет в файле `processing_status.json`:

```json
{
  "created_at": "2024-01-01T00:00:00",
  "last_updated": "2024-01-01T12:00:00",
  "processing_sessions": {
    "session_20240101_120000": {
      "status": "completed",
      "total_employees": 10,
      "processed_count": 9,
      "failed_count": 1
    }
  },
  "employees": {
    "344": {
      "employee_name": "Иванов Иван",
      "status": "processed",
      "pdf_file_id": "1ABC...XYZ",
      "last_processed": "2024-01-01T12:00:00"
    }
  }
}
```

## 🚨 Обработка ошибок

Система обрабатывает различные типы ошибок:
- Проблемы с подключением к Google API
- Ошибки при создании PDF
- Проблемы с загрузкой в Drive
- Некорректные данные сотрудников

Все ошибки логируются и отображаются в интерфейсе.

## 🔒 Безопасность

- Service Account ключи должны храниться в безопасном месте
- Не коммитьте `.env` файл в репозиторий
- Используйте принцип минимальных привилегий для Google API
- Регулярно ротируйте API ключи

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь в корректности настроек в `.env`
3. Проверьте права доступа Service Account
4. Посмотрите статистику в веб-интерфейсе

## 📝 Лицензия

Этот проект создан для внутреннего использования компании.

---

**Версия:** 1.0.0  
**Дата создания:** 2024-01-01  
**Автор:** HR System Team
