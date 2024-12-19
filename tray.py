import threading
from PIL import Image
import pystray
import sys
import os
from tkinter import messagebox
from schedule_manager import ScheduleManager

icon_instance = None

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_image():
    icon_path = resource_path('images/icon.ico')
    image = Image.open(icon_path)
    image = image.resize((64, 64), Image.LANCZOS)
    return image

def on_quit(icon, item, app):
    icon.stop()
    app.quit()

def show_window(icon, item, app):
    # icon.stop()
    app.after(0, app.deiconify)

def setup_tray(app):
    global icon_instance
    if icon_instance is not None:
        return
    
    image = create_image()
    
    def cancel_schedule():
        ScheduleManager.clear_schedule()
        messagebox.showinfo("Thông Báo", "Đã hủy lịch tự động")
    
    menu = pystray.Menu(
        pystray.MenuItem('Show', lambda icon, item: show_window(icon, item, app)),
        pystray.MenuItem('Cancel Schedule', lambda icon, item: cancel_schedule()),
        pystray.MenuItem('Quit', lambda icon, item: on_quit(icon, item, app))
    )
    
    icon_instance = pystray.Icon("SMBoardAuto", image, "SMBoardAuto", menu)
    threading.Thread(target=icon_instance.run, daemon=True).start()
