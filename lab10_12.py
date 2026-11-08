import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Обробка та аналіз даних (Інкапсуляція роботи з файлом і чисельних операцій) 
class FinancialDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_and_clean_data(self):
        """Завантаження даних із перевіркою виключень та очищенням"""
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"Файл '{self.file_path}' не знайдено в директорії.")
            
            # Читання CSV-файлу
            self.df = pd.read_csv(self.file_path)
            print("[ІНФО] Файл успішно завантажено.")
            
            # Перевірка обов'язкових стовпців
            required_columns = ['Date', 'Asset_Price', 'Volume']
            for col in required_columns:
                if col not in self.df.columns:
                    raise ValueError(f"У файлі відсутній обов'язковий стовпець: '{col}'")
            
            # Конвертація дат та сортування
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            self.df = self.df.sort_values('Date').reset_index(drop=True)
            
            # Заповнення пропусків (якщо є) та розрахунок додаткових показників (дохідність, ковзне середнє)
            self.df['Asset_Price'] = self.df['Asset_Price'].ffill()
            self.df['Daily_Return'] = self.df['Asset_Price'].pct_change() * 100
            self.df['MA_20'] = self.df['Asset_Price'].rolling(window=20).mean() # Ковзне середнє за 20 днів
            
            print("[ІНФО] Попередня обробка та розрахунок показників завершені успішно.")
            return self.df

        except FileNotFoundError as fnf_error:
            print(f"[ПОМИЛКА] {fnf_error}")
            sys.exit(1)
        except ValueError as val_error:
            print(f"[ПОМИЛКА] Помилка формату даних: {val_error}")
            sys.exit(1)
        except Exception as e:
            print(f"[ПОМИЛКА] Сталася непередбачена помилка: {e}")
            sys.exit(1)


# Візуалізація та створення інтерактивного дашборду (Plotly) 
class DashboardVisualizer:
    def __init__(self, df):
        self.df = df

    def create_dashboard(self, output_html="Звітна сторінка.html"):
        """Створення комплексного інтерактивного дашборду з кількома графіками та збереженням у HTML"""
        try:
            # Створюємо сітку суб-графіків (2 рядки, 1 стовпчик)
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=('Динаміка ціни активу та тренд (MA 20)', 'Щоденна процентна дохідність (%) та обсяги торгів')
            )

            # 1. Графік ціни та ковзного середнього
            fig.add_trace(
                go.Scatter(x=self.df['Date'], y=self.df['Asset_Price'], name='Ціна активу', line=dict(color='royalblue', width=2)),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=self.df['Date'], y=self.df['MA_20'], name='MA 20 (Тренд)', line=dict(color='orange', width=1.5, dash='dash')),
                row=1, col=1
            )

            # 2. Графік щоденної дохідності (стовпчикова діаграма)
            colors = ['green' if val >= 0 else 'red' for val in self.df['Daily_Return'].fillna(0)]
            fig.add_trace(
                go.Bar(x=self.df['Date'], y=self.df['Daily_Return'], name='Дохідність (%)', marker_color=colors),
                row=2, col=1
            )

            # Налаштування макету дашборду
            fig.update_layout(
                title_text='<b>Інтерактивний фінансовий дашборд (Варіант 19)</b>',
                title_x=0.5,
                template='plotly_white',
                height=700,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            # Оновлення осей
            fig.update_xaxes(title_text='Дата', row=2, col=1)
            fig.update_yaxes(title_text='Ціна ($)', row=1, col=1)
            fig.update_yaxes(title_text='Зміна (%)', row=2, col=1)

            # Збереження результату у зовнішній файл (HTML-звіт)
            fig.write_html(output_html)
            print(f"[УСПІХ] Інтерактивний дашборд успішно збережено у файл '{output_html}'.")
            
            # Відображення у браузері (за бажанням)
            fig.show()

        except Exception as e:
            print(f"[ПОМИЛКА] Не вдалося створити або зберегти дашборд: {e}")


# ГОЛОВНИЙ БЛОК ВИКОНАННЯ ПРОГРАМИ 
if __name__ == "__main__":
    print("=== ЗАПУСК ПРОГРАМИ АНАЛІЗУ ФІНАНСОВИХ ДАНИХ (ВАРІАНТ 19) ===")
    
    # Генерація тестового файлу даних для демонстрації (якщо файл відсутній)
    sample_filename = "Звітна таблиця.csv"
    if not os.path.exists(sample_filename):
        dates = pd.date_range(start="2024-01-01", periods=100, freq='B')
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100) * 1.5)
        volumes = np.random.randint(10000, 50000, size=100)
        sample_df = pd.DataFrame({'Date': dates, 'Asset_Price': prices, 'Volume': volumes})
        sample_df.to_csv(sample_filename, index=False)
        print(f"[ІНФО] Створено демонстраційний файл '{sample_filename}'.")

    # Ініціалізація та виконання етапів через класи ООП
    processor = FinancialDataProcessor(sample_filename)
    cleaned_data = processor.load_and_clean_data()
    
    # Виведення перших рядків опрацьованих даних у консоль
    print("\n--- Перші 5 рядків опрацьованого DataFrame ---")
    print(cleaned_data.head())

    # Побудова та збереження дашборду
    visualizer = DashboardVisualizer(cleaned_data)
    visualizer.create_dashboard("Звітна сторінка.html")
