import winreg

BASE_REGISTRY_PATH = r"Software\SMBoardAutomation"

def read_settings():
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, BASE_REGISTRY_PATH, 0, winreg.KEY_READ)
        username = winreg.QueryValueEx(registry_key, "Username")[0]
        password = winreg.QueryValueEx(registry_key, "Password")[0]
        category = winreg.QueryValueEx(registry_key, "Category")[0]
        detail = winreg.QueryValueEx(registry_key, "Detail")[0]
        start_with_windows = bool(winreg.QueryValueEx(registry_key, "StartWithWindows")[0])
        winreg.CloseKey(registry_key)
    except FileNotFoundError:
        username = ''
        password = ''
        category = ''
        detail = ''
        start_with_windows = False  # Giá trị mặc định nếu không tìm thấy
    except Exception as e:
        print(f"Lỗi khi đọc cấu hình từ Registry: {e}")
        username = ''
        password = ''
        category = ''
        detail = ''
        start_with_windows = False
    return username, password, category, detail, start_with_windows

def save_settings(username, password, category, detail, start_with_windows):
    try:
        registry_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, BASE_REGISTRY_PATH)
        winreg.SetValueEx(registry_key, "Username", 0, winreg.REG_SZ, username)
        winreg.SetValueEx(registry_key, "Password", 0, winreg.REG_SZ, password)
        winreg.SetValueEx(registry_key, "Category", 0, winreg.REG_SZ, category)
        winreg.SetValueEx(registry_key, "Detail", 0, winreg.REG_SZ, detail)
        winreg.SetValueEx(registry_key, "StartWithWindows", 0, winreg.REG_DWORD, int(start_with_windows))
        winreg.CloseKey(registry_key)
        print("Cấu hình đã được lưu vào Registry.")
    except Exception as e:
        print(f"Lỗi khi lưu cấu hình vào Registry: {e}")
