import tkinter as tk
from tkinter import messagebox, scrolledtext
from schedule_manager import ScheduleManager
from settings import read_settings, save_settings
from automation import automate_task
from tray import setup_tray
import threading
import schedule
from datetime import datetime
import customtkinter as ctk
import winreg
import sys
import os
import win10toast
class AutomationToolApp:
    def __init__(self, root):
        # Configure the root window
        self.root = root
        self.root.title("SmBoard Automation")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')

        # Set up custom theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize variables
        self.username, self.password, self.category, self.detail, self.start_with_windows = read_settings()
        self.function_var = tk.StringVar(value='immediate')
        self.day_vars = {day: tk.BooleanVar() for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
        self.note_var = tk.BooleanVar(value=False)

        # Create main notebook
        self.create_notebook()

        # Gán sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_notebook(self):
        # Main notebook with stylish tabs
        self.notebook = ctk.CTkTabview(self.root, width=550, height=650)
        self.notebook.pack(padx=20, pady=20, fill="both", expand=True)

        # Create tabs
        self.tool_tab = self.notebook.add("Automation")
        self.login_tab = self.notebook.add("Login")
        self.other_tab = self.notebook.add("Settings")
        self.schedule_tab = self.notebook.add("Schedules")  # Thêm tab Schedules

        # Populate tabs
        self.create_login_tab()
        self.create_tool_tab()
        self.create_other_tab()
        self.create_schedule_tab()  # Thêm hàm tạo tab Schedules

    def create_schedule_tab(self):
        # Schedule tab layout
        frame = ctk.CTkFrame(self.schedule_tab)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Label
        ctk.CTkLabel(frame, text="Current Schedule", font=('Arial', 14, 'bold')).pack(pady=10)

        # Textbox to display schedule
        self.schedule_display = scrolledtext.ScrolledText(frame, height=20, width=80, state='disabled')
        self.schedule_display.pack(padx=10, pady=10)

        # Refresh button
        refresh_btn = ctk.CTkButton(frame, text="Refresh", command=self.display_current_schedule)
        refresh_btn.pack(pady=5)

        # Delete Schedule button
        delete_btn = ctk.CTkButton(frame, text="Delete Current Schedule", fg_color="red", command=self.delete_current_schedule)
        delete_btn.pack(pady=5)

        # Initial display
        self.display_current_schedule()

    def display_current_schedule(self):
        """Hiển thị lịch trình hiện tại trong textbox"""
        schedule_info = ScheduleManager.get_current_schedule()
        self.schedule_display.configure(state='normal')
        self.schedule_display.delete("1.0", tk.END)

        if schedule_info:
            schedule_type = schedule_info.get('type', 'N/A')
            time_str = schedule_info.get('time', 'N/A')
            login_details = schedule_info.get('login_details', {})
            note_text = schedule_info.get('note_text', 'N/A')
            if schedule_type == 'recurring':
                days = ', '.join(schedule_info.get('days', []))
                schedule_text = (
                    f"Type: Recurring\n"
                    f"Time: {time_str}\n"
                    f"Days: {days}\n"
                    f"Username: {login_details.get('username', 'N/A')}\n"
                    f"Password: {login_details.get('password', 'N/A')}\n"
                    f"Category: {login_details.get('category', 'N/A')}\n"
                    f"Detail: {login_details.get('detail', 'N/A')}\n"
                    f"Note: {note_text}\n"
                )
            else:
                schedule_text = (
                    f"Type: Scheduled\n"
                    f"Time: {time_str}\n"
                    f"Username: {login_details.get('username', 'N/A')}\n"
                    f"Password: {login_details.get('password', 'N/A')}\n"
                    f"Category: {login_details.get('category', 'N/A')}\n"
                    f"Detail: {login_details.get('detail', 'N/A')}\n"
                    f"Note: {note_text}\n"
                )
            self.schedule_display.insert(tk.END, schedule_text)
        else:
            self.schedule_display.insert(tk.END, "No schedule set.")

        self.schedule_display.configure(state='disabled')

    def delete_current_schedule(self):
        """Xóa lịch trình hiện tại"""
        answer = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa lịch trình hiện tại không?")
        if answer:
            ScheduleManager.clear_schedule()
            self.display_current_schedule()
            messagebox.showinfo("Thông báo", "Đã xóa lịch trình hiện tại.")

    def create_login_tab(self):
        # Login tab layout with improved styling
        frame = ctk.CTkFrame(self.login_tab)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        labels = ['Username', 'Password', 'Category', 'Detail']
        entries = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(frame, text=label, font=('Arial', 12, 'bold')).grid(row=i, column=0, padx=10, pady=10, sticky='w')
            
            if label == 'Password':
                entries[label] = ctk.CTkEntry(frame, width=300, show="*")
            else:
                entries[label] = ctk.CTkEntry(frame, width=300)
            
            entries[label].grid(row=i, column=1, padx=10, pady=10)
            
            # Pre-fill entries
            if label == 'Username':
                entries[label].insert(0, self.username)
            elif label == 'Password':
                entries[label].insert(0, self.password)
            elif label == 'Category':
                entries[label].insert(0, self.category)
            elif label == 'Detail':
                entries[label].insert(0, self.detail)

        # Password visibility toggle
        show_password_btn = ctk.CTkButton(
            frame, 
            text='Show Password', 
            command=lambda: self.toggle_password(entries['Password'], show_password_btn)
        )
        show_password_btn.grid(row=4, column=1, padx=10, pady=10, sticky='w')

        # Save button
        save_btn = ctk.CTkButton(
            frame, 
            text='Save Credentials', 
            command=lambda: self.save_login_details(entries)
        )
        save_btn.grid(row=5, column=1, padx=10, pady=10, sticky='e')

    def create_tool_tab(self):
        # Automation tool tab with modern design
        frame = ctk.CTkFrame(self.tool_tab)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Execution mode selection
        modes = [
            ('Immediate Execution', 'immediate'),
            ('Scheduled Execution', 'scheduled'),
            ('Recurring Execution', 'recurring')
        ]

        for i, (text, value) in enumerate(modes):
            ctk.CTkRadioButton(
                frame, 
                text=text, 
                variable=self.function_var, 
                value=value, 
                command=self.update_tool_ui
            ).grid(row=i, column=0, padx=10, pady=10, sticky='w')

        # Placeholder for dynamic content
        self.tool_dynamic_frame = ctk.CTkFrame(frame)
        self.tool_dynamic_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Initial UI update
        self.update_tool_ui()

    def create_other_tab(self):
        # Additional settings tab
        frame = ctk.CTkFrame(self.other_tab)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Note section
        note_check = ctk.CTkCheckBox(
            frame, 
            text="Enable Additional Notes", 
            variable=self.note_var, 
            command=self.toggle_note
        )
        note_check.pack(padx=10, pady=10, anchor='w')

        self.note_text = ctk.CTkTextbox(frame, height=200, width=500)
        self.note_text.pack(padx=10, pady=10)
        self.note_text.pack_forget()

        # Startup with Windows section
        startup_check = ctk.CTkCheckBox(
            frame,
            text="Start with Windows",
            variable=tk.BooleanVar(value=self.start_with_windows),
            command=self.toggle_start_with_windows
        )
        # Gán biến cho checkbox để có thể truy cập sau
        self.startup_var = tk.BooleanVar(value=self.start_with_windows)
        startup_check.configure(variable=self.startup_var, command=self.toggle_start_with_windows)
        startup_check.pack(padx=10, pady=10, anchor='w')

    def toggle_password(self, entry, button):
        # Toggle password visibility
        current_show = entry.cget('show')
        new_show = '' if current_show == '*' else '*'
        entry.configure(show=new_show)
        button.configure(text='Show Password' if new_show == '*' else 'Hide Password')

    def save_login_details(self, entries):
        # Save login details
        username = entries['Username'].get()
        password = entries['Password'].get()
        category = entries['Category'].get()
        detail = entries['Detail'].get()

        # Lấy trạng thái start_with_windows
        start_with_windows = self.startup_var.get()

        save_settings(username, password, category, detail, start_with_windows)
        messagebox.showinfo("Success", "Login details saved successfully!")

        # Cập nhật registry
        if start_with_windows:
            self.add_to_startup()
        else:
            self.remove_from_startup()

    def update_tool_ui(self):
        # Clear previous dynamic content
        for widget in self.tool_dynamic_frame.winfo_children():
            widget.destroy()

        mode = self.function_var.get()

        if mode == 'immediate':
            start_btn = ctk.CTkButton(
                self.tool_dynamic_frame, 
                text='Execute Now', 
                command=self.start_immediate_automation
            )
            start_btn.pack(padx=10, pady=10)

        elif mode in ['scheduled', 'recurring']:
            # Frame for time selection
            time_frame = ctk.CTkFrame(self.tool_dynamic_frame)
            time_frame.pack(padx=10, pady=10)

            # Hour selection
            hour_label = ctk.CTkLabel(time_frame, text="Hour")
            hour_label.pack(side='left', padx=5)
            hour_combo = ctk.CTkComboBox(
                time_frame, 
                values=[f'{i:02d}' for i in range(24)], 
                width=70
            )
            hour_combo.set('00')  # Default value
            hour_combo.pack(side='left', padx=5)

            # Minute selection
            minute_label = ctk.CTkLabel(time_frame, text="Minute")
            minute_label.pack(side='left', padx=5)
            minute_combo = ctk.CTkComboBox(
                time_frame, 
                values=[f'{i:02d}' for i in range(60)], 
                width=70
            )
            minute_combo.set('00')  # Default value
            minute_combo.pack(side='left', padx=5)

            if mode == 'recurring':
                day_frame = ctk.CTkFrame(self.tool_dynamic_frame)
                day_frame.pack(padx=10, pady=10)
                
                for day in self.day_vars:
                    ctk.CTkCheckBox(
                        day_frame, 
                        text=day, 
                        variable=self.day_vars[day]
                    ).pack(side='left', padx=5)

            start_btn = ctk.CTkButton(
                self.tool_dynamic_frame, 
                text='Schedule Task', 
                command=lambda: self.start_scheduled_automation(
                    f"{hour_combo.get()}:{minute_combo.get()}"
                )
            )
            start_btn.pack(padx=10, pady=10)

    def toggle_note(self):
        if self.note_var.get():
            self.note_text.pack(padx=10, pady=10)
        else:
            self.note_text.pack_forget()

    def toggle_start_with_windows(self):
        start_with_windows = self.startup_var.get()
        save_settings(
            self.username, 
            self.password, 
            self.category, 
            self.detail, 
            start_with_windows
        )
        if start_with_windows:
            self.add_to_startup()
        else:
            self.remove_from_startup()

    def add_to_startup(self):
        """Thêm ứng dụng vào registry để khởi động cùng Windows"""
        try:
            if getattr(sys, 'frozen', False):
                # Nếu ứng dụng được đóng gói bằng PyInstaller
                exe_path = sys.executable
            else:
                # Chạy script Python
                exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "SMBoardAutomation", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            messagebox.showinfo("Thông Báo", "Đã thêm ứng dụng vào khởi động cùng Windows.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm vào khởi động cùng Windows: {e}")

    def remove_from_startup(self):
        """Loại bỏ ứng dụng khỏi registry khởi động cùng Windows"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_ALL_ACCESS
            )
            winreg.DeleteValue(key, "SMBoardAutomation")
            winreg.CloseKey(key)
            messagebox.showinfo("Thông Báo", "Đã loại bỏ ứng dụng khỏi khởi động cùng Windows.")
        except FileNotFoundError:
            # Nếu không tìm thấy, không làm gì
            pass
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể loại bỏ khỏi khởi động cùng Windows: {e}")

    def start_immediate_automation(self):
        # Lấy thông tin từ login tab
        login_frame = self.login_tab.winfo_children()[0]
        username_val = login_frame.winfo_children()[1].get()  # Username entry
        password_val = login_frame.winfo_children()[3].get()  # Password entry
        category_val = login_frame.winfo_children()[5].get()  # Category entry
        detail_val = login_frame.winfo_children()[7].get()    # Detail entry

        # Lưu cài đặt
        save_settings(username_val, password_val, category_val, detail_val, self.startup_var.get())

        # Lấy nội dung ghi chú nếu được bật
        note_text = self.note_text.get("1.0", tk.END).strip() if self.note_var.get() else None

        # Chạy automation trong luồng riêng
        threading.Thread(
            target=automate_task, 
            args=(username_val, password_val, category_val, detail_val, note_text), 
            daemon=True
        ).start()

        messagebox.showinfo("Thông báo", "Đang thực hiện khai báo ngay lập tức")

    def start_scheduled_automation(self, time_str):
        try:
            # Truy xuất giá trị từ login tab
            login_frame = self.login_tab.winfo_children()[0]
            username_val = login_frame.winfo_children()[1].get()
            password_val = login_frame.winfo_children()[3].get()
            category_val = login_frame.winfo_children()[5].get()
            detail_val = login_frame.winfo_children()[7].get()

            # Kiểm tra thông tin đăng nhập
            if not all([username_val, password_val, category_val, detail_val]):
                raise ValueError("Vui lòng điền đầy đủ thông tin đăng nhập!")

            # Kiểm tra và lưu thông tin
            save_settings(username_val, password_val, category_val, detail_val, self.startup_var.get())

            # Kiểm tra và lấy ghi chú (nếu có)
            note_text = None
            if self.note_var.get():
                note_text = self.note_text.get("1.0", tk.END).strip()

            # Kiểm tra định dạng thời gian
            try:
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except:
                raise ValueError("Định dạng thời gian không hợp lệ. Vui lòng nhập theo định dạng HH:MM")

            # Lấy trạng thái của việc lên lịch
            schedule_type = self.function_var.get()

            # Tạo job function
            def scheduled_job():
                try:
                    current_time = datetime.now().strftime('%H:%M')
                    print(f"Đang thực hiện công việc tự động lúc {current_time}")
                    threading.Thread(
                        target=automate_task,
                        args=(username_val, password_val, category_val, detail_val, note_text),
                        daemon=True
                    ).start()
                    
                    # Hiển thị thông báo
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(
                        "SMBoard Automation",
                        f"Đang thực hiện khai báo tự động",
                        duration=5
                    )
                except Exception as e:
                    print(f"Lỗi khi thực hiện công việc tự động: {str(e)}")

            # Lưu thông tin lịch trình
            if schedule_type == 'recurring':
                days = [day for day, var in self.day_vars.items() if var.get()]
                
                if not days:
                    raise ValueError("Vui lòng chọn ít nhất một ngày trong tuần")

                # Xóa các job cũ
                schedule.clear()

                # Tạo job mới cho các ngày đã chọn
                def recurring_job():
                    current_day = datetime.now().strftime('%A')
                    if current_day in days:
                        scheduled_job()

                schedule.every().day.at(time_str).do(recurring_job)

                # Lưu lịch trình lặp lại
                ScheduleManager.save_schedule(
                    'recurring', 
                    time_str, 
                    days, 
                    {
                        'username': username_val,
                        'password': password_val,
                        'category': category_val,
                        'detail': detail_val
                    },
                    note_text
                )

                messagebox.showinfo("Thông báo", f"Đã lên lịch chạy các ngày: {', '.join(days)} lúc {time_str}")

            else:
                # Xóa các job cũ
                schedule.clear()

                # Tạo job mới
                schedule.every().day.at(time_str).do(scheduled_job)

                # Lưu lịch trình một lần
                ScheduleManager.save_schedule(
                    'scheduled', 
                    time_str, 
                    login_details={
                        'username': username_val,
                        'password': password_val,
                        'category': category_val,
                        'detail': detail_val
                    },
                    note_text=note_text
                )

                messagebox.showinfo("Thông báo", f"Đã lên lịch chạy hàng ngày lúc {time_str}")

            # Ẩn cửa sổ chính và chuyển sang system tray
            self.root.withdraw()
            setup_tray(self.root)

            # Bắt đầu scheduler trong thread riêng
            ScheduleManager.start_scheduler()

            # Cập nhật hiển thị lịch trình
            self.display_current_schedule()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    # def display_current_schedule(self):
    #     """Hiển thị thông tin lịch trình hiện tại"""
    #     try:
    #         schedule_data = ScheduleManager.load_schedule()
    #         if schedule_data:
    #             schedule_type = schedule_data.get('Type')
    #             time_str = schedule_data.get('Time')
    #             days = schedule_data.get('Days', '').split(',') if schedule_data.get('Days') else []
                
    #             status_text = ""
    #             if schedule_type == 'recurring':
    #                 status_text = f"Lịch hiện tại: Chạy vào các ngày {', '.join(days)} lúc {time_str}"
    #             else:
    #                 status_text = f"Lịch hiện tại: Chạy hàng ngày lúc {time_str}"
                
    #             # Hiển thị trong tooltip của system tray
    #             self.update_tray_tooltip(status_text)
                
    #             return status_text
    #     except Exception as e:
    #         print(f"Lỗi khi hiển thị lịch trình: {str(e)}")
    #         return "Không có lịch trình nào đang chạy"

    def update_tray_tooltip(self, text):
        """Cập nhật tooltip cho system tray icon"""
        try:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.title = text
        except:
            pass

    def on_closing(self):
        """Xử lý sự kiện khi người dùng nhấn nút X"""
        try:
            schedule_data = ScheduleManager.load_schedule()
            if schedule_data:
                self.root.withdraw()
                messagebox.showinfo(
                    "Thông báo",
                    "Ứng dụng đã ẩn vào system tray và sẽ tiếp tục chạy theo lịch.\n"
                    "Để thoát hoàn toàn, hãy nhấp chuột phải vào biểu tượng tray và chọn 'Quit'."
                )
            else:
                if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát không?"):
                    self.root.destroy()
        except Exception as e:
            print(f"Lỗi khi đóng ứng dụng: {str(e)}")
            self.root.destroy()

    # def on_closing(self):
    #     """Xử lý sự kiện khi người dùng nhấn nút X"""
    #     self.root.withdraw()  # Ẩn cửa sổ chính
    #     messagebox.showinfo("Thông báo", "Ứng dụng đã ẩn vào system tray. Để thoát hoàn toàn, hãy nhấp chuột phải vào biểu tượng tray và chọn 'Quit'.")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    root = ctk.CTk()
    
    # Khởi động tray icon
    app = AutomationToolApp(root)
    setup_tray(root)
    
    # Khôi phục lịch trình (nếu có)
    restored = ScheduleManager.restore_schedule()
    if restored:
        print("Đã khôi phục lịch trình thành công.")
        ScheduleManager.start_scheduler()  # Khởi động luồng lịch trình
        messagebox.showinfo("Thông báo", "Lịch trình đã được khôi phục và đang chạy.")
    else:
        print("Không có lịch trình nào để khôi phục.")
        messagebox.showinfo("Thông báo", "Không có lịch trình nào để khôi phục.")
    
    root.mainloop()

if __name__ == "__main__":
    main()

