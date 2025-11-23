from myproject import scraper, saver

def main():
    # 1. Получаем данные с сайта (все страницы раздела)
    print("Начинаем парсинг всех страниц раздела...")
    # Увеличиваем задержку между страницами до 5 секунд, чтобы избежать блокировки
    data = scraper.scrape_all_pages(
        "https://www.divan.ru/category/svet?sort=0", 
        headless=False, 
        max_pages=50,
        delay_between_pages=5  # Задержка 5 секунд между страницами
    )
    
    if not data:
        print("Внимание: Данные не получены! Проверьте подключение к интернету и доступность сайта.")
        return
    
    print(f"Найдено товаров: {len(data)}")
    
    # 2. Сохраняем в разные форматы
    print("Сохраняем данные...")
    saver.save_all(data)  # Сохраняет в results.csv, results.json, results.xlsx
    saver.render_html(data, filename="results.html")
    
    print("\nПервые 3 товара:")
    for item in data[:3]:
        print(f"  - {item.get('name', 'Нет названия')}: {item.get('price', 'Нет цены')} {item.get('currency', '')}")
    
    print(f"\nДанные сохранены в папку: {saver.OUTPUT_DIR.absolute()}")
    print("Файлы: results.csv, results.json, results.xlsx, results.html")


if __name__ == "__main__":
    main()
