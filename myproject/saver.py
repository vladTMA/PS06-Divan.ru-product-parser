# saver.py
import csv, json, pandas as pd
from jinja2 import Template
from pathlib import Path
import time

# Директория для сохранения файлов.
# Используем абсолютный путь относительно файла saver.py
OUTPUT_DIR = Path(__file__).parent / "output"

# Единый порядок полей
FIELDS = ["name", "price", "currency", "url", "instock_text"]

# Русские названия для заголовков
HEADER_NAMES = {
    "name": "Название",
    "price": "Цена",
    "currency": "Валюта",
    "url": "Ссылка",
    "instock_text": "Наличие"
}

def save_csv(data, filename="results.csv"):
    if not data:
        print("Предупреждение: Нет данных для сохранения в CSV")
        return
    filepath = OUTPUT_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    print(f"Сохраняем CSV в: {filepath.absolute()}")
    
    # Определяем поля из данных (используем только те, что есть в данных)
    available_fields = []
    if data:
        # Берем поля из первого элемента
        available_fields = [field for field in FIELDS if field in data[0]]
        # Если в данных есть поля, которых нет в FIELDS, добавляем их
        for key in data[0].keys():
            if key not in FIELDS and key not in available_fields:
                available_fields.append(key)
    
    # Используем доступные поля или все FIELDS, если данные полные
    fields_to_use = available_fields if available_fields else FIELDS
    fieldnames = [HEADER_NAMES.get(field, field) for field in fields_to_use]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:  # data = список словарей от парсера
            writer.writerow({
                HEADER_NAMES.get(field, field): item.get(field, "")
                for field in fields_to_use
            })


def save_json(data, filename="results.json"):
    if not data:
        print("Предупреждение: Нет данных для сохранения в JSON")
        return
    filepath = OUTPUT_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    print(f"Сохраняем JSON в: {filepath.absolute()}")
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_xlsx(data, filename="results.xlsx"):
    if not data:
        print("Предупреждение: Нет данных для сохранения в XLSX")
        return
    filepath = OUTPUT_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    print(f"Сохраняем XLSX в: {filepath.absolute()}")
    
    try:
        df = pd.DataFrame(data)
        # Определяем поля, которые есть в данных
        available_fields = [field for field in FIELDS if field in df.columns]
        # Если есть все поля из FIELDS, используем их, иначе используем все доступные
        if available_fields == FIELDS:
            df = df[FIELDS]
            df.rename(columns=HEADER_NAMES, inplace=True)
        else:
            # Используем только доступные поля
            df = df[available_fields]
            df.rename(columns={k: HEADER_NAMES.get(k, k) for k in available_fields}, inplace=True)
        df.to_excel(filepath, index=False)
    except PermissionError:
        print(f"ОШИБКА: Файл {filepath.name} открыт в другой программе.")
        print("Закройте файл и попробуйте снова, или файл будет пропущен.")
        temp_filename = f"results_{int(time.time())}.xlsx"
        temp_filepath = OUTPUT_DIR / temp_filename
        df.to_excel(temp_filepath, index=False)
        print(f"Файл сохранен с временным именем: {temp_filename}")
    except Exception as e:
            print(f"Не удалось сохранить XLSX файл: {e}")


def render_html(data, filename="results.html"):
    if not data:
        print("Предупреждение: Нет данных для сохранения в HTML")
        return None
    filepath = OUTPUT_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    template = """
       <html>
       <head>
           <title>Парсинг результатов</title>
           <meta charset="utf-8">
           <style>
               table { border-collapse: collapse; width: 100%; }
               th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
               th { background-color: #4CAF50; color: white; }
               tr:nth-child(even) { background-color: #f2f2f2; }
               a { color: #0066cc; }
           </style>
       </head>
       <body>
           <h1>Результаты парсинга</h1>
           <table>
               <tr>
               {% for field in fields %}
                   <th>{{ header_names[field] }}</th>
               {% endfor %}
               </tr>
               {% for row in data %}
               <tr>
               {% for field in fields %}
                   <td>
                   {% if field == 'url' %}
                       <a href="{{ row.get(field, '') }}">{{ row.get(field, '') }}</a>
                   {% else %}
                       {{ row.get(field, '') or '—' }}
                   {% endif %}
                   </td>
               {% endfor %}
               </tr>
               {% endfor %}
           </table>
       </body>
       </html>
    """
    html = Template(template).render(data=data, fields=FIELDS, header_names=HEADER_NAMES)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML файл сохранен: {filepath.absolute()}")
    return str(filepath)


def save_all(data):
    save_csv(data)
    save_json(data)
    save_xlsx(data)
    render_html(data)
