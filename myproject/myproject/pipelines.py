# pipelines.py
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pandas as pd
import json, csv, os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class MyprojectPipeline:
    def process_item(self, item, spider):
        return item

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class SavePipeline:
    def open_spider(self, spider):
        self.data = []

    def close_spider(self, spider):
        # Сохраняем в CSV
        csv_path = os.path.join(OUTPUT_DIR, "results.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "link"])
            writer.writeheader()
            writer.writerows(self.data)

        # Сохраняем в JSON
        json_path = os.path.join(OUTPUT_DIR, "results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        # Сохраняем в XLSX
        xlsx_path = os.path.join(OUTPUT_DIR, "results.xlsx")
        df = pd.DataFrame(self.data)
        df.to_excel(xlsx_path, index=False)

        # Сохраняем HTML
        html_path = os.path.join(OUTPUT_DIR, "results.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<html><body><h1>Результаты парсинга</h1><table border='1'>")
            f.write("<tr><th>Название</th><th>Цена</th><th>Ссылка</th></tr>")
            for row in self.data:
                f.write(f"<tr><td>{row['name']}</td><td>{row['price']}</td><td>{row['currency']}</td><td><a href='{row['url']}'>{row['url']}</a><td>{row['instock_text']}</td></td></tr>")
            f.write("</table></body></html>")

    def process_item(self, item, spider):
        self.data.append(dict(item))
        return item

