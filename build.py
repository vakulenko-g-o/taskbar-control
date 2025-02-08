import PyInstaller.__main__
import sys
from pathlib import Path

try:
    # Путь к текущей директории проекта
    base_path = Path(__file__).parent
    icon_path = base_path / 'assets' / 'icon.ico'
    
    # Параметры сборки
    params = [
        'taskbar_control.py',  # Основной файл
        '--name=TaskbarControl',  # Имя выходного файла
        '--onefile',  # Собрать в один файл
        '--windowed',  # Оконное приложение (без консоли)
        f'--icon={icon_path}',  # Иконка приложения
        '--clean',  # Очистить временные файлы
        '--add-data', f'{base_path / "assets"}/*;assets',  # Добавить папку assets
        '--hidden-import=PIL',
        '--hidden-import=pystray',
        '--hidden-import=win32gui',
        '--hidden-import=win32con',
        '--hidden-import=win32api',
        '--hidden-import=keyboard'
    ]

    print("Начало сборки...")
    PyInstaller.__main__.run(params)
    print("Сборка завершена успешно!")

except Exception as e:
    print(f"Ошибка при сборке: {e}")
    sys.exit(1)