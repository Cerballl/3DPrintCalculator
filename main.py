import customtkinter as ctk
import json
import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class CostCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор 3D Друку")
        self.geometry("900x650")
        self.minsize(800, 600)

        self.iconbitmap(resource_path("icon.ico"))

        self.history_file = "print_history.json"
        self.history_data = self.load_history()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.input_frame, text="Параметри моделі", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        self.name_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Назва моделі", width=300)
        self.name_entry.pack(pady=5, padx=20)

        self.weight_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Вага моделі (г)", width=300)
        self.weight_entry.pack(pady=5, padx=20)

        self.time_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Час друку (годин)", width=300)
        self.time_entry.pack(pady=5, padx=20)

        ctk.CTkLabel(self.input_frame, text="Фінансові налаштування", font=ctk.CTkFont(size=16, weight="bold")).pack(
            pady=15)

        self.spool_price_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ціна котушки 1 кг (грн)", width=300)
        self.spool_price_entry.pack(pady=5, padx=20)

        self.hour_price_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ціна за 1 годину роботи (грн)",
                                             width=300)
        self.hour_price_entry.pack(pady=5, padx=20)

        self.kwh_price_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Тариф на світло (грн/кВт)", width=300)
        self.kwh_price_entry.pack(pady=5, padx=20)

        self.power_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Споживання принтера (кВт)", width=300)
        self.power_entry.pack(pady=5, padx=20)
        self.power_entry.insert(0, "0.08")

        self.markup_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Націнка (%)", width=300)
        self.markup_entry.pack(pady=5, padx=20)

        self.calc_btn = ctk.CTkButton(self.input_frame, text="Розрахувати та Зберегти", command=self.calculate,
                                      width=300, height=40)
        self.calc_btn.pack(pady=25)

        self.result_label = ctk.CTkLabel(self.input_frame, text="", font=ctk.CTkFont(size=16, weight="bold"),
                                         text_color="#2FA572")
        self.result_label.pack(pady=5)

        self.history_frame = ctk.CTkFrame(self)
        self.history_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.history_frame, text="Історія підрахунків", font=ctk.CTkFont(size=20, weight="bold")).pack(
            pady=15)

        self.scrollable_history = ctk.CTkScrollableFrame(self.history_frame)
        self.scrollable_history.pack(fill="both", expand=True, padx=10, pady=10)

        self.render_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history_data, f, ensure_ascii=False, indent=4)

    def calculate(self):
        try:
            name = self.name_entry.get() or "Без назви"
            weight = float(self.weight_entry.get().replace(',', '.'))
            time_hrs = float(self.time_entry.get().replace(',', '.'))
            spool_price = float(self.spool_price_entry.get().replace(',', '.'))
            hour_price = float(self.hour_price_entry.get().replace(',', '.'))
            kwh_price = float(self.kwh_price_entry.get().replace(',', '.'))
            power = float(self.power_entry.get().replace(',', '.'))
            markup = float(self.markup_entry.get().replace(',', '.'))

            price_per_gram = spool_price / 1000
            material_cost = weight * price_per_gram
            time_cost = time_hrs * hour_price
            electricity_cost = time_hrs * power * kwh_price

            base_cost = material_cost + time_cost + electricity_cost
            final_price = base_cost + (base_cost * markup / 100)

            result_text = (f"Собівартість: {base_cost:.2f} грн\n"
                           f"Ціна для продажу: {final_price:.2f} грн")
            self.result_label.configure(text=result_text)

            entry = {
                "name": name,
                "weight": weight,
                "time": time_hrs,
                "material_cost": round(material_cost, 2),
                "base_cost": round(base_cost, 2),
                "final_price": round(final_price, 2)
            }
            self.history_data.append(entry)
            self.save_history()
            self.render_history()

        except ValueError:
            self.result_label.configure(text="Помилка: перевірте, чи скрізь введені числа!", text_color="red")

    def render_history(self):
        for widget in self.scrollable_history.winfo_children():
            widget.destroy()

        for i, item in enumerate(reversed(self.history_data)):
            original_idx = len(self.history_data) - 1 - i

            frame = ctk.CTkFrame(self.scrollable_history, fg_color=("gray85", "gray20"))
            frame.pack(fill="x", pady=5, padx=5)

            info = (f"📦 {item['name']} | {item['weight']}г | {item['time']}год\n"
                    f"Собівартість: {item['base_cost']} грн  ➡️  Продаж: {item['final_price']} грн")

            lbl = ctk.CTkLabel(frame, text=info, justify="left")
            lbl.pack(side="left", padx=15, pady=10)

            del_btn = ctk.CTkButton(frame, text="Видалити", width=60, fg_color="#C62828", hover_color="#8E0000",
                                    command=lambda idx=original_idx: self.delete_entry(idx))
            del_btn.pack(side="right", padx=15)

    def delete_entry(self, idx):
        del self.history_data[idx]
        self.save_history()
        self.render_history()


if __name__ == "__main__":
    app = CostCalculator()
    app.mainloop()