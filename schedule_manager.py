import winreg
import threading
import schedule
import time
from datetime import datetime
from automation import automate_task
import win10toast
import json

BASE_REGISTRY_PATH = r"Software\SMBoardAutomation"
SCHEDULE_REGISTRY_PATH = r"Software\SMBoardAutomation\Schedule"

class ScheduleManager:
    scheduler_running = False

    @classmethod
    def save_schedule(cls, schedule_type, time_str, days=None, login_details=None, note_text=None):
        """Lưu thông tin lịch trình vào Registry"""
        schedule_info = {
            'type': schedule_type,
            'time': time_str,
            'days': days,
            'login_details': login_details,
            'note_text': note_text
        }
        try:
            registry_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, SCHEDULE_REGISTRY_PATH)
            winreg.SetValueEx(registry_key, "ScheduleInfo", 0, winreg.REG_SZ, json.dumps(schedule_info))
            winreg.CloseKey(registry_key)
            print("Lịch trình đã được lưu vào Registry.")
        except Exception as e:
            print(f"Lỗi khi lưu lịch trình: {e}")

    @classmethod
    def load_schedule(cls):
        """Tải thông tin lịch trình từ Registry"""
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, SCHEDULE_REGISTRY_PATH, 0, winreg.KEY_READ)
            schedule_info_json = winreg.QueryValueEx(registry_key, "ScheduleInfo")[0]
            winreg.CloseKey(registry_key)
            return json.loads(schedule_info_json)
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Lỗi khi tải lịch trình: {e}")
            return None

    @classmethod
    def clear_schedule(cls):
        """Xóa lịch trình đã lưu khỏi Registry"""
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, SCHEDULE_REGISTRY_PATH)
            schedule.clear()
            print("Đã xóa lịch trình khỏi Registry và dọn dẹp các công việc đã lên lịch.")
        except FileNotFoundError:
            print("Không tìm thấy khóa lịch trình để xóa.")
            pass
        except Exception as e:
            print(f"Lỗi khi xóa lịch trình: {e}")

    @classmethod
    def get_current_schedule(cls):
        """Lấy thông tin lịch trình hiện tại từ Registry"""
        schedule_info = cls.load_schedule()
        if not schedule_info:
            return None
        return schedule_info

    @classmethod
    def restore_schedule(cls):
        """Khôi phục lịch trình từ Registry"""
        schedule_info = cls.load_schedule()
        if not schedule_info:
            print("Không tìm thấy lịch trình nào để khôi phục.")
            return False

        try:
            schedule_type = schedule_info.get('type')
            time_str = schedule_info.get('time')
            login_details = schedule_info.get('login_details', {})
            note_text = schedule_info.get('note_text', None)

            if schedule_type == 'recurring':
                days = schedule_info.get('days', [])

                def recurring_job():
                    current_day = datetime.now().strftime('%A')
                    if current_day in days:
                        threading.Thread(
                            target=automate_task,
                            args=(
                                login_details.get('username'),
                                login_details.get('password'),
                                login_details.get('category'),
                                login_details.get('detail'),
                                note_text
                            ),
                            daemon=True
                        ).start()

                        # Thông báo
                        toaster = win10toast.ToastNotifier()
                        toaster.show_toast(
                            "Automation Tool",
                            f"Đã thực hiện khai báo tự động lúc {datetime.now().strftime('%H:%M')}",
                            duration=5
                        )

                schedule.every().day.at(time_str).do(recurring_job)

            else:
                def scheduled_job():
                    threading.Thread(
                        target=automate_task,
                        args=(
                            login_details.get('username'),
                            login_details.get('password'),
                            login_details.get('category'),
                            login_details.get('detail'),
                            note_text
                        ),
                        daemon=True
                    ).start()

                    # Thông báo
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(
                        "Automation Tool",
                        f"Đã thực hiện khai báo tự động lúc {datetime.now().strftime('%H:%M')}",
                        duration=5
                    )

                    # Xóa lịch trình sau khi thực hiện nếu là một lần
                    cls.clear_schedule()

                schedule.every().day.at(time_str).do(scheduled_job)

            print("Đã khôi phục lịch trình từ Registry.")
            return True

        except Exception as e:
            print(f"Lỗi khôi phục lịch trình: {e}")
            return False

    @classmethod
    def start_scheduler(cls):
        """Bắt đầu luồng lịch trình"""
        if cls.scheduler_running:
            # print("Scheduler đã đang chạy.")
            return

        def run_scheduler():
            # print("Scheduler thread started.")
            while True:
                schedule.run_pending()
                time.sleep(1)

        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        cls.scheduler_running = True
        print("Scheduler đã được khởi động.")
