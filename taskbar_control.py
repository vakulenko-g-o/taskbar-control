import argparse
import ctypes
import winreg
import sys
import os
import threading
from typing import Optional
import win32gui
import win32con
from PIL import Image
import pystray
from pystray import MenuItem as item
import keyboard
from pathlib import Path
from logger import setup_logger
import win32api
import signal

logger = setup_logger()

class TaskbarController:
    def __init__(self):
        self.HOTKEY = 'ctrl+alt+t'
        self.icon_path = Path(__file__).parent / 'assets' / 'icon.png'
        self.is_autohide_enabled = self.get_current_autohide_state()
        self.icon: Optional[pystray.Icon] = None
        self.hotkey_thread = None
        self.running = True  # Add control flag
        self._setup_signal_handlers()
        self.setup_tray()
        self.register_hotkey()
        logger.info(f"TaskbarController initialized with hotkey: {self.HOTKEY}, current autohide state: {self.is_autohide_enabled}")

    def _setup_signal_handlers(self):
        """Регистрация обработчиков сигналов"""
        signal.signal(signal.SIGTERM, self._handle_exit)
        signal.signal(signal.SIGINT, self._handle_exit)

    def _handle_exit(self, signum, frame):
        """Корректное завершение при получении сигнала"""
        logger.info(f"Received signal {signum}")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Очистка ресурсов перед выходом"""
        try:
            self.running = False  # Stop status checking
            keyboard.unhook_all()
            if self.icon:
                self.icon.stop()
            if self.hotkey_thread and self.hotkey_thread.is_alive():
                self.hotkey_thread.join(timeout=1.0)
            # Убираем попытку удаления иконки, так как она может использоваться
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_current_autohide_state(self) -> bool:
        try:
            taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
            
            class APPBARDATA(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("hWnd", ctypes.c_void_p),
                    ("uCallbackMessage", ctypes.c_ulong),
                    ("uEdge", ctypes.c_ulong),
                    ("rc", ctypes.c_long * 4),
                    ("lParam", ctypes.c_long)
                ]
            
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(abd)
            abd.hWnd = taskbar
            
            # 0x00000004 - команда для получения текущего состояния
            state = ctypes.windll.shell32.SHAppBarMessage(0x00000004, ctypes.byref(abd))
            # Проверяем бит ABS_AUTOHIDE (0x0000001)
            is_autohide = bool(state & 0x0000001)
            logger.info(f"Current taskbar state checked: autohide={is_autohide}")
            return is_autohide
            
        except Exception as e:
            logger.error(f"Failed to get taskbar state: {e}")
            return False

    def update_tooltip(self) -> str:
        status = "включено" if self.is_autohide_enabled else "выключено"
        return f"Автоскрытие панели задач: {status}\nГорячие клавиши: {self.HOTKEY}"

    def setup_tray(self) -> None:
        try:
            icon_path = Path(__file__).parent / 'assets' / 'icon.png'
            # Принудительно пересоздаем иконку
            if (icon_path.exists()):
                icon_path.unlink()
            self._create_default_icon(icon_path)
            
            self.icon = pystray.Icon(
                "Taskbar Controller",
                Image.open(icon_path),
                menu=self.create_menu(),
                title=self.update_tooltip()  # Добавляем подсказку
            )
            logger.info("Tray icon setup completed")
        except Exception as e:
            logger.error(f"Failed to setup tray: {e}")
            sys.exit(1)

    def _create_default_icon(self, path: Path) -> None:
        try:
            path.parent.mkdir(exist_ok=True)
            # Создаем изображение 128x128 для лучшего качества
            size = 128
            img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
            
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Рисуем градиентный фон
            from PIL import ImageEnhance
            circle = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
            circle_draw = ImageDraw.Draw(circle)
            margin = 8
            circle_draw.ellipse([margin, margin, size-margin, size-margin], 
                              fill='#1976D2')  # Darker Material Blue
            
            # Добавляем тень
            shadow = ImageEnhance.Brightness(circle).enhance(0.7)
            img.paste(shadow, (2, 2), shadow)
            img.paste(circle, (0, 0), circle)
            
            # Рисуем полоски панели задач
            bar_height = 12
            bar_margin = 35
            bar_spacing = 16
            bar_colors = ['#FFFFFF', '#F5F5F5', '#EEEEEE']  # Разные оттенки белого
            
            for i, y in enumerate(range(45, 85, bar_spacing)):
                if i < len(bar_colors):
                    draw.rounded_rectangle(
                        [bar_margin, y, size-bar_margin, y+bar_height],
                        radius=4,
                        fill=bar_colors[i]
                    )
            
            # Сохраняем с максимальным качеством
            img.save(path, quality=95)
            logger.info(f"Created new custom icon at {path}")
        except Exception as e:
            logger.error(f"Failed to create icon: {e}")
            # Создаем простую иконку в случае ошибки
            img = Image.new('RGB', (64, 64), color='#2196F3')
            img.save(path)

    def create_menu(self):
        menu_text = 'Выключить автоскрытие' if self.is_autohide_enabled else 'Включить автоскрытие'
        return (
            item(menu_text, self.toggle_taskbar_autohide),
            item('Выход', self.quit_app)
        )

    def toggle_taskbar_autohide(self, icon=None, item=None) -> bool:
        try:
            taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
            
            class APPBARDATA(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("hWnd", ctypes.c_void_p),
                    ("uCallbackMessage", ctypes.c_ulong),
                    ("uEdge", ctypes.c_ulong),
                    ("rc", ctypes.c_long * 4),
                    ("lParam", ctypes.c_long)
                ]
            
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(abd)
            abd.hWnd = taskbar
            
            self.is_autohide_enabled = not self.is_autohide_enabled
            abd.lParam = 0x0000001 if self.is_autohide_enabled else 0x0000002
            
            result = ctypes.windll.shell32.SHAppBarMessage(0x0000A, ctypes.byref(abd))
            logger.info(f"Taskbar state changed: autohide={'enabled' if self.is_autohide_enabled else 'disabled'}")
            
            # Обновляем меню и подсказку
            self.icon.menu = self.create_menu()
            self.icon.title = self.update_tooltip()
            
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to toggle taskbar: {e}")
            return False

    def register_hotkey(self) -> None:
        try:
            # Запускаем отдельный поток для горячих клавиш
            self.hotkey_thread = threading.Thread(target=self._hotkey_worker, daemon=True)
            self.hotkey_thread.start()
            logger.info(f"Hotkey {self.HOTKEY} registered in separate thread")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")

    def _hotkey_worker(self):
        """Работа с горячими клавишами в отдельном потоке"""
        try:
            keyboard.add_hotkey(self.HOTKEY, self.toggle_taskbar_autohide, suppress=True)
            keyboard.wait()  # Бесконечное ожидание нажатий
        except Exception as e:
            logger.error(f"Error in hotkey worker: {e}")

    def _check_hotkey_status(self) -> None:
        """Периодическая проверка работоспособности горячих клавиш"""
        try:
            if not self.running:
                return
            if not keyboard.is_pressed(self.HOTKEY.split('+')[0]):
                # Если горячие клавиши не работают, перерегистрируем их
                keyboard.unhook_all()
                keyboard.add_hotkey(self.HOTKEY, self.toggle_taskbar_autohide, suppress=True)
                logger.info("Hotkeys re-registered successfully")
        except Exception as e:
            logger.error(f"Error checking hotkey status: {e}")
        finally:
            if self.running:
                # Используем threading.Timer вместо queue.after
                threading.Timer(5.0, self._check_hotkey_status).start()

    def quit_app(self, icon=None, item=None) -> None:
        logger.info("Application shutdown initiated")
        self.cleanup()
        os._exit(0)

    def run(self) -> None:
        try:
            # Проверяем права администратора
            if not self._is_admin():
                logger.warning("Application running without admin rights, some features might be limited")
            logger.info("Starting application")
            # Запускаем первую проверку горячих клавиш
            self._check_hotkey_status()
            self.icon.run()
        except Exception as e:
            logger.error(f"Critical error during runtime: {e}")
            self.cleanup()
            sys.exit(1)

    @staticmethod
    def _is_admin():
        """Проверка прав администратора"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

if __name__ == "__main__":
    app = TaskbarController()
    app.run()
