import sys
from cx_Freeze import setup, Executable
from pathlib import Path

# Базовый путь к проекту
base_path = Path(__file__).parent

try:
    # Файлы для включения в сборку
    include_files = [
        (base_path / "assets", "assets"),
        (base_path / "logger.py", "logger.py")
    ]

    # Зависимости
    build_exe_options = {
        "packages": ["win32gui", "win32con", "win32api", "PIL", "pystray", "keyboard"],
        "include_files": include_files,
        "include_msvcr": True,
        "excludes": ["msilib"]  # Исключаем проблемный модуль
    }

    # Настройка GUI приложения
    base = "Win32GUI" if sys.platform == "win32" else None

    setup(
        name="TaskbarControl",
        version="1.0",
        description="Утилита управления панелью задач Windows",
        options={"build_exe": build_exe_options},
        executables=[
            Executable(
                "taskbar_control.py",
                base=base,
                target_name="TaskbarControl.exe",
                icon="assets/icon.ico"
            )
        ]
    )
except Exception as e:
    print(f"Ошибка при сборке: {e}")