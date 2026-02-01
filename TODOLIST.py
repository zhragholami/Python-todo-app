import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import sys


class TODOLIST:
    def __init__(self):
        try:
            print("در حال راه اندازی برنامه")
            self.window = tk.Tk()
            self.window.title("برنامه مدیریت کارها")
            self.window.geometry("850x600")
            self.window.configure(bg='#f0f0f0')
            self.font_family = self.get_safe_font()
            print(f"فونت انتخاب شده: {self.font_family}")

            print("در حال اتصال به دیتابیس")
            self.init_database()
            self.tasks = self.load_tasks_from_db()
            self.filtered_tasks = self.tasks[:]  # لیست فیلتر شده
            print(f"{len(self.tasks)} کار بارگیری شد")

            print("در حال ایجاد رابط کاربری")
            self.create_widgets_with_clock()
            print("برنامه با موفقیت راه اندازی شد")

        except Exception as e:
            print(f"خطا در راه اندازی: {e}")
            messagebox.showerror("خطا", f"برنامه اجرا نشد\n{str(e)}")
            sys.exit(1)

    def get_safe_font(self):
        safe_font = ["Tahoma", "Arial", "Segoe UI", "Microsoft Sans Serif", "B Nazanin"]
        import tkinter.font as tkfont
        available_fonts = tkfont.families()
        for font in safe_font:
            if font in available_fonts:
                return font
        return available_fonts[0] if available_fonts else "TkDefaultFont"

    def init_database(self):
        try:
            self.db_path = "TODOLIST.db"
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'جدید',
                    created_at TEXT,
                    last_updated TEXT
                )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"خطا در دیتابیس: {e}")
            raise

    def load_tasks_from_db(self):
        try:
            self.cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
            rows = self.cursor.fetchall()
            tasks = []
            for row in rows:
                create_time = "00:00"
                if row[3]:
                    try:
                        dt = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
                        create_time = dt.strftime("%H:%M")
                    except:
                        create_time = row[3][11:16] if len(row[3]) > 10 else "00:00"

                update_time = "00:00"
                if row[4]:
                    try:
                        dt = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
                        update_time = dt.strftime("%H:%M")
                    except:
                        update_time = row[4][11:16] if len(row[4]) > 10 else "00:00"

                tasks.append({
                    'id': row[0],
                    'title': row[1],
                    'status': row[2],
                    'create_time': create_time,
                    'update_time': update_time,
                    'full_created': row[3],
                    'full_updated': row[4]
                })
            return tasks
        except Exception as e:
            print(f"خطا در بارگیری کارها: {e}")
            return []

    def create_widgets_with_clock(self):
        # Header Frame
        header_frame = tk.Frame(self.window, bg='#f0f0f0', height=90)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)

        # Title Frame
        title_frame = tk.Frame(header_frame, bg='#2C3E50')
        title_frame.place(x=20, y=20)

        tk.Label(
            title_frame,
            text="برنامه مدیریت کارها",
            font=(self.font_family, 18, "bold"),
            bg='#2C3E50',
            fg='white',
        ).pack()

        tk.Label(
            title_frame,
            text="مدیریت کارهای روزانه شما",
            font=(self.font_family, 10),
            bg='#2C3E50',
            fg='#BDC3C7',
        ).pack()

        # Clock Frame
        clock_frame = tk.Frame(header_frame, bg='#34495E')
        clock_frame.place(relx=1, x=-20, y=20, anchor='ne')

        self.date_label = tk.Label(
            clock_frame,
            font=(self.font_family, 11),
            bg='#34495E',
            fg='#ECF0F1',
        )
        self.date_label.pack(anchor='e')

        self.clock_label = tk.Label(
            clock_frame,
            font=("Courier New", 16, "bold"),
            bg='#34495E',
            fg='#1ABC9C',
        )
        self.clock_label.pack(anchor='e')

        self.update_datetime()

        # Main Frame
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=(20, 0))

        # Input Frame
        input_frame = tk.Frame(main_frame, bg='#f0f0f0', pady=15)
        input_frame.pack(fill='x')

        tk.Label(
            input_frame,
            text="کار جدید ➕",
            font=(self.font_family, 13),
            bg='#f0f0f0',
        ).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.task_entry = tk.Entry(
            input_frame,
            font=(self.font_family, 13),
            width=35
        )
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)

        add_button = tk.Button(
            input_frame,
            text="اضافه کردن",
            font=(self.font_family, 11, "bold"),
            bg='#27AE60',
            fg='white',
            command=self.add_task,
            padx=20,
            pady=6,
        )
        add_button.grid(row=0, column=2, padx=10, pady=5)

        # Filter Frame
        filter_frame = tk.Frame(main_frame, bg='#ECF0F1', relief='groove', bd=2)
        filter_frame.pack(fill='x', pady=(10, 10), padx=5)

        tk.Label(
            filter_frame,
            text="🔍 فیلتر بر اساس وضعیت:",
            font=(self.font_family, 11, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50',
        ).pack(side='left', padx=(15, 10), pady=10)

        # ایجاد دکمه‌های فیلتر
        self.filter_var = tk.StringVar(value="همه")

        filter_buttons = [
            ("همه 📋", "همه", "#3498DB"),
            ("جدید ⭕", "جدید", "#E74C3C"),
            ("در حال انجام 🟡", "در حال انجام", "#F39C12"),
            ("انجام شده ✅", "انجام شده", "#27AE60")
        ]

        for text, value, color in filter_buttons:
            btn = tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                font=(self.font_family, 10, "bold"),
                bg='#ECF0F1',
                fg='#2C3E50',
                selectcolor='#D5DBDB',
                activebackground='#ECF0F1',
                command=self.apply_filter,
                indicatoron=0,
                width=15,
                relief='raised'
            )
            btn.pack(side='left', padx=5)

            # تغییر رنگ دکمه انتخاب شده
            if value == "همه":
                btn.config(bg='#3498DB', fg='white', activebackground='#2980B9')
            elif value == "جدید":
                btn.config(bg='#FADBD8', fg='#C0392B', activebackground='#F5B7B1')
            elif value == "در حال انجام":
                btn.config(bg='#FDEBD0', fg='#D35400', activebackground='#F8C471')
            elif value == "انجام شده":
                btn.config(bg='#D5F4E6', fg='#27AE60', activebackground='#ABEBC6')

        # دکمه بازنشانی فیلتر
        reset_btn = tk.Button(
            filter_frame,
            text="🗑️ پاک کردن فیلتر",
            font=(self.font_family, 9),
            bg='#95A5A6',
            fg='white',
            command=self.reset_filter,
            padx=10,
            pady=3,
        )
        reset_btn.pack(side='right', padx=(0, 15))

        # List Frame
        list_frame = tk.Frame(main_frame, bg='#f0f0f0')
        list_frame.pack(fill='both', expand=True, pady=(5, 0))

        columns = ('ردیف', 'عنوان کار', 'وضعیت', 'زمان ایجاد', 'آخرین ویرایش')
        self.task_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=12,
        )

        column_widths = {
            'ردیف': 60,
            'عنوان کار': 280,
            'وضعیت': 130,
            'زمان ایجاد': 110,
            'آخرین ویرایش': 110,
        }

        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=column_widths[col], anchor='center')

        # استایل برای Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=(self.font_family, 10, "bold"))
        style.configure("Treeview", font=(self.font_family, 10), rowheight=30)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        self.task_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Button Frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0', pady=15)
        button_frame.pack(fill='x')

        buttons = [
            ("تغییر وضعیت", '#3498DB', self.change_status),
            ("ویرایش", '#9B59B6', self.edit_task),
            ("حذف", '#E74C3C', self.delete_task),
            ("پاک کردن همه", '#95A5A6', self.clear_all_tasks),
        ]

        for text, color, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=(self.font_family, 11),
                bg=color,
                fg='white',
                command=command,
                padx=15,
                pady=7,
            )
            btn.pack(side='left', padx=5)

        info_button = tk.Button(
            button_frame,
            text='📊 اطلاعات',
            font=(self.font_family, 11, "bold"),
            bg='#34495E',
            fg='white',
            command=self.show_info,
            padx=15,
            pady=7,
        )
        info_button.pack(side='left', padx=5)

        # Stats Frame
        stats_frame = tk.Frame(
            main_frame,
            bg='#ECF0F1',
            relief='ridge',
            bd=1,
        )
        stats_frame.pack(side='bottom', fill='x', pady=(10, 0))

        self.stats_label = tk.Label(
            stats_frame,
            text="در حال بارگیری آمار...",
            font=(self.font_family, 11),
            bg='#ECF0F1',
            fg='#2C3E50',
            padx=15,
            pady=10,
        )
        self.stats_label.pack()

        if not self.tasks:
            self.add_sample_tasks()

        self.apply_filter()
        self.task_tree.bind('<Double-Button-1>', self.on_double_click)

    def update_datetime(self):
        now = datetime.now()
        current_date = now.strftime("%Y/%m/%d")
        current_time = now.strftime("%H:%M:%S")

        self.date_label.config(text=f"{current_date}")
        self.clock_label.config(text=f"{current_time}")

        if int(now.second) % 2 == 0:
            self.clock_label.config(fg='#1ABC9C')
        else:
            self.clock_label.config(fg='#3498DB')

        self.window.after(1000, self.update_datetime)

    def add_sample_tasks(self):
        sample_tasks = [
            ("نمونه کار ۱ - خرید مواد غذایی", "جدید"),
            ("نمونه کار ۲ - انجام پروژه برنامه نویسی", "در حال انجام"),
            ("نمونه کار ۳ - مراجعه به دکتر", "انجام شده"),
            ("نمونه کار ۴ - مطالعه کتاب", "جدید"),
            ("نمونه کار ۵ - ورزش روزانه", "انجام شده"),
        ]

        for title, status in sample_tasks:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                '''INSERT INTO tasks(title, status, created_at, last_updated) 
                VALUES (?, ?, ?, ?)''',
                (title, status, current_time, current_time)
            )

        self.conn.commit()
        self.tasks = self.load_tasks_from_db()
        self.filtered_tasks = self.tasks[:]
        print(f"{len(sample_tasks)} کار نمونه اضافه شد")

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute(
                    '''INSERT INTO tasks(title, status, created_at, last_updated) 
                    VALUES (?, ?, ?, ?)''',
                    (task_text, 'جدید', current_time, current_time)
                )
                self.conn.commit()
                self.tasks = self.load_tasks_from_db()
                self.task_entry.delete(0, tk.END)
                self.apply_filter()  # بعد از اضافه کردن، فیلتر را اعمال کن
                messagebox.showinfo("موفق", f"کار '{task_text}' اضافه شد")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در ذخیره کار: {str(e)}")
        else:
            messagebox.showwarning("هشدار", "لطفا عنوان کار را وارد کنید")

    def apply_filter(self):
        """اعمال فیلتر بر اساس وضعیت انتخاب شده"""
        filter_type = self.filter_var.get()

        if filter_type == "همه":
            self.filtered_tasks = self.tasks[:]
        else:
            self.filtered_tasks = [task for task in self.tasks if task['status'] == filter_type]

        self.refresh_task_list()
        self.update_stats()

    def reset_filter(self):
        """بازنشانی فیلتر به حالت همه"""
        self.filter_var.set("همه")
        self.apply_filter()

    def refresh_task_list(self):
        """تازه‌سازی لیست کارها"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        if not self.filtered_tasks:
            # نمایش پیام اگر لیست خالی است
            self.task_tree.insert('', 'end', values=(
                "-",
                "هیچ کاری با این فیلتر یافت نشد",
                "-",
                "-",
                "-"
            ))
            return

        for i, task in enumerate(self.filtered_tasks, 1):
            status_icons = {
                'جدید': '⭕',
                'در حال انجام': '🟡',
                'انجام شده': '✅'
            }
            icon = status_icons.get(task['status'], '⭕')

            created_time = task['create_time']
            updated_time = task['update_time']

            if task['full_created'] == task['full_updated']:
                updated_display = "---"
            else:
                updated_display = updated_time

            tag = ""
            if task['status'] == 'جدید':
                tag = "new"
            elif task['status'] == 'در حال انجام':
                tag = "doing"
            elif task['status'] == 'انجام شده':
                tag = "done"

            item_id = self.task_tree.insert('', 'end', values=(
                i,
                task['title'],
                f"{icon} {task['status']}",
                created_time,
                updated_display
            ), tags=(tag,))

            # تنظیم رنگ برای ردیف‌ها
            self.task_tree.tag_configure('new', background='#FADBD8')
            self.task_tree.tag_configure('doing', background='#FDEBD0')
            self.task_tree.tag_configure('done', background='#D5F4E6')

    def update_stats(self):
        """به‌روزرسانی آمار"""
        total = len(self.tasks)
        new_count = sum(1 for t in self.tasks if t['status'] == 'جدید')
        doing_count = sum(1 for t in self.tasks if t['status'] == 'در حال انجام')
        done_count = sum(1 for t in self.tasks if t['status'] == 'انجام شده')

        filtered_count = len(self.filtered_tasks)
        filter_type = self.filter_var.get()

        current_time = datetime.now().strftime("%H:%M:%S")

        self.stats_label.config(
            text=f"📊 آمار: {total} کل کارها | {new_count} جدید | {doing_count} در حال انجام | {done_count} انجام شده | 🔍 نمایش: {filtered_count} ({filter_type}) | 🕐 {current_time}"
        )

    def change_status(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفا یک کار را انتخاب کنید")
            return
        if self.task_tree.item(selected[0])['values'][1] == "هیچ کاری با این فیلتر یافت نشد":
            return

        # پیدا کردن کار اصلی در لیست tasks
        item = self.task_tree.item(selected[0])
        filtered_index = item['values'][0] - 1

        if 0 <= filtered_index < len(self.filtered_tasks):
            filtered_task = self.filtered_tasks[filtered_index]

            # پیدا کردن همان کار در لیست اصلی
            task_id = filtered_task['id']
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task:
                status_map = {
                    'جدید': 'در حال انجام',
                    'در حال انجام': 'انجام شده',
                    'انجام شده': 'جدید'
                }

                current_status = task['status']
                new_status = status_map.get(current_status, 'جدید')
                updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    self.cursor.execute(
                        'UPDATE tasks SET status=?, last_updated=? WHERE id=?',
                        (new_status, updated_time, task_id)
                    )
                    self.conn.commit()

                    task['status'] = new_status
                    task['update_time'] = updated_time[11:16]
                    task['full_updated'] = updated_time

                    self.apply_filter()  # بعد از تغییر وضعیت، فیلتر را اعمال کن
                    messagebox.showinfo("موفق", f"وضعیت تغییر کرد به: {new_status}")
                except Exception as e:
                    messagebox.showerror("خطا", f"خطا در تغییر وضعیت: {str(e)}")

    def edit_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفا یک کار را انتخاب کنید")
            return
        if self.task_tree.item(selected[0])['values'][1] == "هیچ کاری با این فیلتر یافت نشد":
            return
        item = self.task_tree.item(selected[0])
        filtered_index = item['values'][0] - 1
        if 0 <= filtered_index < len(self.filtered_tasks):
            filtered_task = self.filtered_tasks[filtered_index]
            old_title = filtered_task['title']

            # پیدا کردن همان کار در لیست اصلی
            task_id = filtered_task['id']
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task:
                edit_window = tk.Toplevel(self.window)
                edit_window.title("ویرایش کار")
                edit_window.geometry("400x200")
                edit_window.configure(bg='#f0f0f0')

                tk.Label(
                    edit_window,
                    text="ویرایش عنوان کار",
                    font=(self.font_family, 14, "bold"),
                    bg='#f0f0f0',
                    pady=20
                ).pack()

                entry = tk.Entry(
                    edit_window,
                    font=(self.font_family, 12),
                    width=40,
                )
                entry.pack(pady=20)
                entry.insert(0, old_title)
                entry.focus()

                def save_edit():
                    new_title = entry.get().strip()
                    if new_title and new_title != old_title:
                        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        try:
                            self.cursor.execute(
                                'UPDATE tasks SET title=?, last_updated=? WHERE id=?',
                                (new_title, update_time, task_id)
                            )
                            self.conn.commit()

                            task['title'] = new_title
                            task['update_time'] = update_time[11:16]
                            task['full_updated'] = update_time

                            self.apply_filter()
                            edit_window.destroy()
                            messagebox.showinfo("موفق", "عنوان کار ویرایش شد")
                        except Exception as e:
                            messagebox.showerror("خطا", f"خطا در ویرایش: {str(e)}")
                    else:
                        messagebox.showwarning("هشدار", "لطفا عنوان کار را وارد کنید")

                tk.Button(
                    edit_window,
                    text="ذخیره",
                    font=(self.font_family, 11, "bold"),
                    bg='#27AE60',
                    fg='white',
                    command=save_edit,
                    padx=20,
                    pady=8,
                ).pack(pady=20)

    def on_double_click(self, event):
        self.edit_task()

    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفا یک کار را انتخاب کنید")
            return

        if self.task_tree.item(selected[0])['values'][1] == "هیچ کاری با این فیلتر یافت نشد":
            return

        item = self.task_tree.item(selected[0])
        filtered_index = item['values'][0] - 1

        if 0 <= filtered_index < len(self.filtered_tasks):
            filtered_task = self.filtered_tasks[filtered_index]
            task_title = filtered_task['title']
            task_id = filtered_task['id']
            task_index = next((i for i, t in enumerate(self.tasks) if t['id'] == task_id), -1)

            if task_index >= 0:
                if messagebox.askyesno("تایید حذف", f"آیا می‌خواهید کار '{task_title}' را حذف کنید؟"):
                    try:
                        self.cursor.execute(
                            'DELETE FROM tasks WHERE id=?',
                            (task_id,)
                        )
                        self.conn.commit()
                        del self.tasks[task_index]
                        self.apply_filter()
                        messagebox.showinfo("موفق", "کار حذف شد")
                    except Exception as e:
                        messagebox.showerror("خطا", f"خطا در حذف کار: {str(e)}")

    def clear_all_tasks(self):
        if not self.tasks:
            messagebox.showinfo("اطلاعات", "لیست کارها خالی است")
            return

        if messagebox.askyesno("تایید پاک کردن", "آیا می‌خواهید همه کارها را پاک کنید؟"):
            try:
                self.cursor.execute('DELETE FROM tasks')
                self.conn.commit()
                self.tasks.clear()
                self.filtered_tasks.clear()
                self.apply_filter()
                messagebox.showinfo("موفق", "همه کارها حذف شدند")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در پاک کردن: {str(e)}")

    def show_info(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y/%m/%d")

        total = len(self.tasks)
        new_count = sum(1 for t in self.tasks if t['status'] == 'جدید')
        doing_count = sum(1 for t in self.tasks if t['status'] == 'در حال انجام')
        done_count = sum(1 for t in self.tasks if t['status'] == 'انجام شده')

        filter_type = self.filter_var.get()
        filtered_count = len(self.filtered_tasks)

        info = f"""📋 برنامه مدیریت کارها

📅 تاریخ: {current_date}
🕐 زمان: {current_time}

📊 آمار کلی:
• کل کارها: {total}
• کارهای جدید: {new_count}
• در حال انجام: {doing_count}
• انجام شده: {done_count}

🔍 وضعیت فیلتر:
• فیلتر فعال: {filter_type}
• تعداد نمایش داده شده: {filtered_count}
"""
        messagebox.showinfo("درباره برنامه", info)

    def run(self):
        try:
            print("برنامه در حال اجراست...")
            self.window.mainloop()
        except Exception as e:
            print(f"خطا در اجرا: {e}")
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()
                print("دیتابیس بسته شد")


if __name__ == '__main__':
    app = TODOLIST()
    app.run()