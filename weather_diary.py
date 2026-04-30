import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

DATA_FILE = "diary_data.json"


class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("750x550")
        self.root.resizable(True, True)

        self.records = []
        self.load_data()

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # === Рамка ввода ===
        input_frame = tk.LabelFrame(self.root, text="Добавить запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Описание
        tk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame, width=25)
        self.desc_entry.grid(row=0, column=5, padx=5, pady=5)

        # Осадки
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=0, column=6, padx=10, pady=5)

        # Кнопка добавить
        tk.Button(input_frame, text="➕ Добавить запись", command=self.add_record, bg="lightgreen").grid(row=0, column=7, padx=10, pady=5)

        # === Рамка фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Температура >").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=8)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(filter_frame, text="°C").grid(row=0, column=4, padx=0, pady=5)

        tk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter, bg="lightblue").grid(row=0, column=5, padx=10, pady=5)
        tk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter, bg="lightgray").grid(row=0, column=6, padx=5, pady=5)

        # === Таблица для записей ===
        columns = ("Дата", "Температура (°C)", "Описание", "Осадки")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # === Кнопки управления ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_data, bg="lightyellow").pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_data_interactive, bg="lightyellow").pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Удалить выбранное", command=self.delete_selected, bg="salmon").pack(side="left", padx=5)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2025-04-30)")
            return

        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        record = {
            "date": date,
            "temperature": temp,
            "description": description,
            "precipitation": precip
        }

        self.records.append(record)
        self.refresh_table()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def refresh_table(self, records_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = records_to_show if records_to_show is not None else self.records
        for rec in data:
            precip_text = "Да" if rec["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                rec["date"],
                rec["temperature"],
                rec["description"],
                precip_text
            ))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.records[:]

        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты для фильтра")
                return
            filtered = [r for r in filtered if r["date"] == filter_date]

        if filter_temp_str:
            try:
                temp_threshold = float(filter_temp_str)
                filtered = [r for r in filtered if r["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура в фильтре должна быть числом")
                return

        self.refresh_table(filtered)
        messagebox.showinfo("Фильтр", f"Показано записей: {len(filtered)}")

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("Фильтр", "Фильтр сброшен")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить выбранную запись?"):
            for item in selected:
                values = self.tree.item(item, "values")
                # Ищем запись по всем полям
                for rec in self.records:
                    if (rec["date"] == values[0] and
                        rec["temperature"] == float(values[1]) and
                        rec["description"] == values[2] and
                        ((rec["precipitation"] and values[3] == "Да") or (not rec["precipitation"] and values[3] == "Нет"))):
                        self.records.remove(rec)
                        break
            self.refresh_table()
            messagebox.showinfo("Удаление", "Запись удалена")

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.records = []

    def load_data_interactive(self):
        self.load_data()
        self.refresh_table()
        messagebox.showinfo("Загрузка", f"Загружено записей: {len(self.records)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
  
