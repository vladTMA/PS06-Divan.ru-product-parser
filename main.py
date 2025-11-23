# main.py
from myproject.scraper import scrape_section
from myproject.saver import save_all, render_html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os


def get_brave_driver():
    options = Options()
    # Указываем путь к Brave
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    # webdriver_manager сам скачает и установит подходящий драйвер
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


if __name__ == "__main__":
    # 1. Парсим данные
    print("Начинаем парсинг...")
    data = scrape_section("https://www.divan.ru/category/svet", headless=False)
    print(f"Получено товаров: {len(data)}")
    
    if not data:
        print("Внимание: Данные не получены! Проверьте подключение к интернету и доступность сайта.")
    else:
        # 2. Сохраняем в CSV/JSON/XLSX
        print("Сохраняем данные...")
        save_all(data)
        print("Данные сохранены в CSV, JSON и XLSX")

        # 3. Генерируем HTML
        html_file = render_html(data)
        print(f"HTML файл создан: {html_file}")

    # 4. Открываем HTML в Brave
    driver = get_brave_driver()
    driver.get(f"file:///{os.path.abspath(html_file)}")
    print("Открыт файл:", driver.title)

    # 5. Закрываем драйвер
    driver.quit()