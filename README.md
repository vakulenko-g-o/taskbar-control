# Taskbar Controller

Утилита для управления автоскрытием панели задач Windows с системным треем и горячими клавишами.

## Возможности

- Управление автоскрытием панели задач через системный трей
- Горячая клавиша (Ctrl+Alt+T) для быстрого переключения
- Логирование операций
- Автозапуск в свернутом режиме

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/taskbar-controller.git
cd taskbar-controller
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

Запустите программу:
```bash
python taskbar_control.py
```

## Структура проекта

```
taskbar_control/
├── assets/
│   └── icon.png
├── logs/
│   └── taskbar_controller.log
├── taskbar_control.py
├── logger.py
├── requirements.txt
└── README.md
```

## Создание EXE-файла

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=assets/icon.ico taskbar_control.py
```
