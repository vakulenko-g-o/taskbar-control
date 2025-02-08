from PIL import Image
from pathlib import Path
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('icon_converter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def convert_to_ico(png_path, ico_path, sizes=[(32, 32), (64, 64), (128, 128)]):
    """Конвертирует PNG в ICO с несколькими размерами"""
    try:
        logger.info(f"Начало конвертации {png_path} в {ico_path}")
        
        # Проверяем существование исходного файла
        if not os.path.exists(png_path):
            logger.error(f"Файл {png_path} не найден")
            raise FileNotFoundError(f"Файл {png_path} не найден")

        # Создаем директорию для ico если её нет
        ico_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Директория {ico_path.parent} создана или уже существует")

        # Открываем изображение
        img = Image.open(png_path)
        logger.info(f"Изображение открыто: размер {img.size}, режим {img.mode}")
        
        # Конвертируем в RGBA если нужно
        if img.mode != 'RGBA':
            logger.info(f"Конвертация из {img.mode} в RGBA")
            img = img.convert('RGBA')

        # Создаем разные размеры иконок
        icon_sizes = []
        for size in sizes:
            logger.debug(f"Создание иконки размером {size}")
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            icon_sizes.append(resized_img)

        # Сохраняем первое изображение как ico
        logger.info(f"Сохранение ICO файла с размерами: {sizes}")
        icon_sizes[0].save(
            ico_path, 
            format='ICO', 
            sizes=[(img.width, img.height) for img in icon_sizes],
            append_images=icon_sizes[1:]
        )
        
        logger.info(f"Иконка успешно сконвертирована и сохранена в {ico_path}")
        return True

    except Exception as e:
        logger.error(f"Ошибка при конвертации: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    try:
        logger.info("Запуск программы конвертации")
        base_path = Path(__file__).parent
        png_path = base_path / 'assets' / 'icon.png'
        ico_path = base_path / 'assets' / 'icon.ico'
        
        result = convert_to_ico(png_path, ico_path)
        if result:
            logger.info("Программа успешно завершена")
        else:
            logger.error("Программа завершилась с ошибкой")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)