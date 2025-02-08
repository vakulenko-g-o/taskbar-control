import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger() -> logging.Logger:
    logger = logging.getLogger('TaskbarController')
    logger.setLevel(logging.INFO)

    # Создаем директорию для логов
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'taskbar_controller.log'

    # Настраиваем ротацию логов
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1 MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Добавляем вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Настраиваем форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger