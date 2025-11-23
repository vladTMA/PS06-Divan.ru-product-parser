# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import time


def scrape():
    """Парсит одну страницу раздела lamp (для теста)."""
    url = "https://www.divan.ru/category/lamp"
    return scrape_section(url, headless=True)

def scrape_all_pages(base_url="https://www.divan.ru/category/svet?sort=0", headless=True, max_pages=50, delay_between_pages=3):
    """
    Проходит по всем страницам раздела divan.ru/свет и возвращает список товаров.

    Args:
        base_url (str): Базовый URL раздела без параметра page.
                        Например: "https://www.divan.ru/category/svet?sort=0"
        headless (bool): Если True, запускает браузер в headless режиме.
        max_pages (int): Максимальное количество страниц для обхода.
        delay_between_pages (int): Задержка между запросами страниц в секундах (по умолчанию 3).

    Returns:
        list[dict]: Список всех товаров из раздела.
    """
    all_results = []
    seen_urls = set()  # Для отслеживания дубликатов между страницами
    
    for page in range(0, max_pages):  # Пагинация начинается с 0
        # Формируем URL с параметром page
        separator = "&" if "?" in base_url else "?"
        url = f"{base_url}{separator}page={page}"
        print(f"\n=== Парсим страницу {page}: {url} ===")
        
        try:
            results = scrape_section(url, headless=headless)
            if not results:
                print(f"Нет данных на странице {page}, останавливаемся.")
                break
            
            # Фильтруем дубликаты между страницами
            new_results = []
            for item in results:
                item_url = item.get("url", "")
                if item_url and item_url not in seen_urls:
                    seen_urls.add(item_url)
                    new_results.append(item)
            
            if new_results:
                all_results.extend(new_results)
                print(f"Добавлено {len(new_results)} новых товаров со страницы {page} (всего: {len(all_results)})")
            else:
                print(f"Все товары со страницы {page} уже были добавлены ранее (дубликаты)")
                # Если все товары дубликаты, возможно, мы дошли до конца
                if page > 0:  # Исправлено: пагинация начинается с 0
                    print("Возможно, достигнут конец раздела.")
                    break
            
            # Добавляем задержку между страницами, чтобы не перегружать сайт
            if page < max_pages - 1:  # Не ждем после последней страницы
                print(f"Ожидание {delay_between_pages} секунд перед следующей страницей...")
                time.sleep(delay_between_pages)
                    
        except Exception as e:
            print(f"Ошибка при парсинге страницы {page}: {e}")
            print(f"Тип ошибки: {type(e).__name__}")
            # Если ошибка связана с переадресацией или блокировкой, делаем большую задержку
            if "redirect" in str(e).lower() or "too many" in str(e).lower():
                print("Обнаружена проблема с переадресацией. Увеличиваем задержку до 10 секунд...")
                time.sleep(10)
            else:
                # Обычная задержка при других ошибках
                time.sleep(delay_between_pages)
            # Продолжаем со следующей страницей
            continue
    
    print(f"\nВсего собрано уникальных товаров: {len(all_results)}")
    return all_results

def scrape_section(url, headless=False, timeout=60):
    """
    Парсит одну страницу раздела divan.ru и возвращает список товаров.

    Args:
        url (str): URL страницы для парсинга. Например:
                   "https://www.divan.ru/category/svet?sort=0&page=0"
        headless (bool): Если True, запускает браузер в headless режиме.
        timeout (int): Таймаут загрузки страницы в секундах.

    Returns:
        list[dict]: Список словарей с данными о товарах:
            - name: название товара
            - price: цена
            - currency: валюта
            - url: ссылка на товар
            - instock_text: текст о наличии
    """

    options = Options()
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    
    # Добавляем User-Agent, режим инкогнито и очистку кэша для избежания блокировки
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--incognito")
    options.add_argument("--disable-cache")
    
    # Оптимизация для ускорения загрузки
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    if headless:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    else:
        # В обычном режиме тоже добавляем размер окна
        options.add_argument("--window-size=1920,1080")
    
    # Используем eager для более быстрой загрузки (не ждем всех ресурсов)
    options.page_load_strategy = 'eager'
    
    print(f"Инициализация ChromeDriver для URL: {url}")
    try:
        # Пробуем использовать webdriver-manager для автоматической загрузки драйвера
        print("Установка ChromeDriver через webdriver-manager...")
        service = Service("chromedriver.exe")  # драйвер лежит в папке проекта
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Ошибка при использовании webdriver-manager: {e}")
        print("Пробуем использовать системный ChromeDriver...")
        # Если webdriver-manager не работает, пробуем системный драйвер
        driver = webdriver.Chrome(options=options)
    
    driver.set_page_load_timeout(timeout)
    
    try:
        print("Загрузка страницы...")
        try:
            driver.get(url)
            # Проверяем, не произошла ли переадресация на страницу ошибки
            current_url = driver.current_url
            page_title = driver.title.lower()
            
            if "too many" in page_title or "redirect" in page_title or "error" in page_title:
                print(f"ВНИМАНИЕ: Возможна проблема с переадресацией!")
                print(f"Текущий URL: {current_url}")
                print(f"Заголовок страницы: {driver.title}")
                return []  # Возвращаем пустой список при проблемах с переадресацией
            
            print(f"Страница загружена. Заголовок: {driver.title}")
        except TimeoutException:
            # Если страница не загрузилась полностью, но частично загрузилась, продолжаем
            print("Предупреждение: Страница загрузилась частично (таймаут page load)")
            print(f"Текущий URL: {driver.current_url}")
        
        # Ждем загрузки страницы с явным ожиданием
        wait = WebDriverWait(driver, timeout)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("Тело страницы найдено")
        except TimeoutException:
            print("Предупреждение: Не удалось дождаться body элемента")
        
        # Прокручиваем страницу постепенно для загрузки всех товаров (lazy loading)
        print("Прокручиваем страницу для загрузки всех товаров...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 10  # Максимум попыток прокрутки
        
        while scroll_attempts < max_scroll_attempts:
            # Прокручиваем вниз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Ждем загрузки новых товаров
            
            # Проверяем, появилась ли новая высота страницы
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Если высота не изменилась, пробуем еще раз
                scroll_attempts += 1
                if scroll_attempts < max_scroll_attempts:
                    time.sleep(1)
                    # Прокручиваем еще немного
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)
            else:
                # Высота изменилась - появились новые товары
                scroll_attempts = 0
                last_height = new_height
                print(f"  Загружено больше товаров, текущая высота страницы: {new_height}px")
        
        # Прокручиваем обратно наверх
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        print("Прокрутка завершена, начинаем поиск карточек товаров...")
        
        # Ждем появления карточек товаров
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[itemtype="http://schema.org/Product"]')))
            print("Карточки товаров обнаружены на странице")
        except TimeoutException:
            print("Предупреждение: Не удалось дождаться появления карточек товаров")
        
        # Пробуем найти карточки по классу ProductCardMain_card__KQzzn
        print("Пробуем селектор: div.ProductCardMain_card__KQzzn")
        lamps = driver.find_elements(By.CSS_SELECTOR, 'div.ProductCardMain_card__KQzzn')
        print(f"Найдено карточек по классу ProductCardMain_card__KQzzn: {len(lamps)}")
        
        # Если нашли карточки по классу, используем их
        if lamps:
            print(f"Используем карточки, найденные по классу ProductCardMain_card__KQzzn")
        else:
            # Если не нашли, пробуем найти через ссылки на товары
            print("Пробуем найти через ссылки link[itemprop='url']")
            url_elements = driver.find_elements(By.CSS_SELECTOR, 'link[itemprop="url"]')
            print(f"Найдено ссылок с itemprop='url': {len(url_elements)}")
            
            if url_elements:
                print(f"Используем ссылки для поиска уникальных карточек")
                lamps = []
                seen_urls = set()
                for url_elem in url_elements:
                    try:
                        # Получаем URL товара
                        product_url = url_elem.get_attribute("href")
                        if product_url and product_url not in seen_urls:
                            seen_urls.add(product_url)
                            # Ищем родительский элемент с классом ProductCardMain_card__KQzzn
                            try:
                                parent = url_elem.find_element(By.XPATH, './ancestor::div[contains(@class, "ProductCardMain_card")][1]')
                                lamps.append(parent)
                            except NoSuchElementException:
                                # Если не нашли по классу, пробуем найти ближайший контейнер карточки
                                try:
                                    parent = url_elem.find_element(By.XPATH, './ancestor::div[contains(@class, "ProductCard") or contains(@class, "Card")][1]')
                                    lamps.append(parent)
                                except NoSuchElementException:
                                    continue
                    except NoSuchElementException:
                        # Если у ссылки нет родителя или href отсутствует
                        continue
                print(f"Найдено уникальных карточек через ссылки: {len(lamps)}")
            
            # Если все еще не нашли, пробуем селектор itemtype
            if not lamps:
                print("Пробуем селектор: div[itemtype='http://schema.org/Product']")
                lamps = driver.find_elements(By.CSS_SELECTOR, 'div[itemtype="http://schema.org/Product"]')
                print(f"Найдено по селектору itemtype: {len(lamps)}")
        
        # Если все еще мало карточек, пробуем найти через div[itemprop='name']
        if len(lamps) <= 1:
            print("Пробуем найти через div[itemprop='name']")
            name_elements = driver.find_elements(By.CSS_SELECTOR, 'div[itemprop="name"]')
            print(f"Найдено элементов с itemprop='name': {len(name_elements)}")
            
            if len(name_elements) > len(lamps):
                print(f"Найдено больше элементов через itemprop='name' ({len(name_elements)}), используем их")
                lamps = []
                seen_urls = set()  # Используем URL для уникальности
                for name_elem in name_elements:
                    try:
                        # Пытаемся найти ссылку на товар в этой карточке
                        try:
                            url_elem = name_elem.find_element(By.XPATH, './ancestor::div[@itemtype="http://schema.org/Product"][1]//link[@itemprop="url"]')
                            product_url = url_elem.get_attribute("href")
                        except NoSuchElementException:
                            # Если не нашли ссылку, пробуем найти родительский контейнер
                            parent = name_elem.find_element(By.XPATH, './ancestor::div[@itemtype="http://schema.org/Product"][1]')
                            try:
                                url_elem = parent.find_element(By.CSS_SELECTOR, 'link[itemprop="url"]')
                                product_url = url_elem.get_attribute("href")
                            except NoSuchElementException:
                                product_url = None
                        
                        # Используем URL для проверки уникальности
                        if product_url and product_url not in seen_urls:
                            seen_urls.add(product_url)
                            # Ищем родительский элемент с itemtype="http://schema.org/Product"
                            try:
                                parent = name_elem.find_element(By.XPATH, './ancestor::div[@itemtype="http://schema.org/Product"][1]')
                                lamps.append(parent)
                            except NoSuchElementException:
                                # Если не нашли родителя с itemtype, пробуем найти любой родительский контейнер
                                try:
                                    parent = name_elem.find_element(By.XPATH, './ancestor::div[contains(@class, "Product") or contains(@class, "Card") or contains(@class, "Item")][1]')
                                    lamps.append(parent)
                                except NoSuchElementException:
                                    continue
                    except NoSuchElementException:
                        continue
                print(f"Найдено уникальных карточек через названия: {len(lamps)}")
        
        if not lamps:
            print("Пробуем селектор: div.ProductCard")
            # Если не нашли по schema.org, пробуем другой селектор
            lamps = driver.find_elements(By.CSS_SELECTOR, 'div.ProductCard')
            print(f"Найдено по второму селектору: {len(lamps)}")
        
        print(f"Итого найдено карточек товаров: {len(lamps)}")
        
        # Дополнительная диагностика: проверяем, сколько элементов с itemprop="name" найдено
        if len(lamps) <= 1:
            print("\n=== ДИАГНОСТИКА ===")
            name_elements_all = driver.find_elements(By.CSS_SELECTOR, 'div[itemprop="name"]')
            print(f"Всего элементов с itemprop='name': {len(name_elements_all)}")
            
            # Пробуем найти все элементы с itemtype
            all_itemtypes = driver.find_elements(By.CSS_SELECTOR, '[itemtype]')
            print(f"Всего элементов с itemtype: {len(all_itemtypes)}")
            
            # Пробуем найти все ссылки с itemprop="url"
            url_elements = driver.find_elements(By.CSS_SELECTOR, 'link[itemprop="url"]')
            print(f"Всего ссылок с itemprop='url': {len(url_elements)}")
            
            if len(name_elements_all) > len(lamps):
                print(f"\nВНИМАНИЕ: Найдено {len(name_elements_all)} элементов с itemprop='name', но только {len(lamps)} карточек!")
                print("Пробуем пересобрать список карточек...")
                lamps = []
                seen_parents = set()
                for name_elem in name_elements_all:
                    try:
                        # Ищем родительский элемент с itemtype="http://schema.org/Product"
                        parent = name_elem.find_element(By.XPATH, './ancestor::div[@itemtype="http://schema.org/Product"][1]')
                        parent_id = id(parent)
                        if parent_id not in seen_parents:
                            lamps.append(parent)
                            seen_parents.add(parent_id)
                    except NoSuchElementException:
                        continue
                print(f"После пересборки найдено карточек: {len(lamps)}")
            print("==================\n")
        
        # Если ничего не найдено, выводим информацию о странице для отладки
        if not lamps:
            print("ВНИМАНИЕ: Карточки товаров не найдены!")
            print(f"URL страницы: {driver.current_url}")
            print(f"Заголовок страницы: {driver.title}")
            # Пробуем найти любые div элементы для диагностики
            all_divs = driver.find_elements(By.TAG_NAME, "div")
            print(f"Всего div элементов на странице: {len(all_divs)}")
            # Пробуем найти элементы с itemprop
            items_with_prop = driver.find_elements(By.CSS_SELECTOR, '[itemprop]')
            print(f"Элементов с атрибутом itemprop: {len(items_with_prop)}")
            if items_with_prop:
                print("Примеры itemprop атрибутов:")
                for item in items_with_prop[:5]:
                    print(f"  - {item.tag_name}: {item.get_attribute('itemprop')}")
        
        if not lamps:
            return []
        results = []
        
        # Используем множество для отслеживания уникальных товаров по URL
        seen_urls = set()
        
        for lamp in lamps:
            try:
                # Сначала получаем URL товара для проверки уникальности
                try:
                    product_url = lamp.find_element(By.CSS_SELECTOR, 'link[itemprop="url"]').get_attribute("href")
                    # Делаем абсолютный URL, если нужно
                    if product_url and not product_url.startswith("http"):
                        product_url = f"https://www.divan.ru{product_url}"
                except NoSuchElementException:
                    product_url = None
                
                # Пропускаем товары без URL или дубликаты
                if not product_url or product_url in seen_urls:
                    if product_url:
                        print(f"Пропущен дубликат: {product_url}")
                    continue
                
                seen_urls.add(product_url)
                
                # Название товара
                try:
                    name_elem = lamp.find_element(By.CSS_SELECTOR, 'div[itemprop="name"]')
                    name = name_elem.text.strip() if name_elem else "нет данных"
                except NoSuchElementException:
                    name = "нет данных"
                
                # Цена - очищаем от HTML комментариев и лишних пробелов
                price_elem = None
                try:
                    price_elem = lamp.find_element(By.CSS_SELECTOR, 'span[data-testid="price"]')
                    price = price_elem.text.strip()
                    # Удаляем лишние пробелы и переносы строк
                    price = ' '.join(price.split())
                except NoSuchElementException:
                    price = "нет данных"

                # Валюта - пробуем несколько вариантов
                currency = "нет данных"
                try:
                    # Вариант 1: Ищем валюту через meta[itemprop="priceCurrency"]
                    try:
                        currency_elem = lamp.find_element(By.CSS_SELECTOR, 'meta[itemprop="priceCurrency"]')
                        currency = currency_elem.get_attribute("content") or "нет данных"
                        if currency and currency != "нет данных":
                            # Преобразуем код валюты в читаемый формат
                            currency_map = {"RUB": "руб.", "USD": "$", "EUR": "€"}
                            currency = currency_map.get(currency, currency)
                    except NoSuchElementException:
                        # Вариант 2: Ищем span.ui-XXdez внутри элемента с ценой
                        if price_elem:
                            try:
                                currency_elem = price_elem.find_element(By.XPATH, './/span[contains(@class, "ui-XXdez")]')
                                currency = currency_elem.text.strip()
                            except NoSuchElementException:
                                # Вариант 3: Ищем span.ui-XXdez в карточке товара
                                currency_elems = lamp.find_elements(By.CSS_SELECTOR, 'span.ui-XXdez')
                                if currency_elems:
                                    currency = currency_elems[0].text.strip()
                        else:
                            # Вариант 4: Ищем span.ui-XXdez в карточке товара
                            currency_elems = lamp.find_elements(By.CSS_SELECTOR, 'span.ui-XXdez')
                            if currency_elems:
                                currency = currency_elems[0].text.strip()
                except Exception as e:
                    print(f"Ошибка при поиске валюты: {e}")
                    currency = "нет данных"
                
                # Текст о наличии
                try:
                    instock_elem = lamp.find_element(By.CSS_SELECTOR, 'div.MainInfo_count__MmnNN')
                    instock_text = instock_elem.text.strip() if instock_elem else "нет данных"
                except NoSuchElementException:
                    instock_text = "нет данных"

                results.append({
                    "name": name,
                    "price": price,
                    "currency": currency,
                    "url": product_url,
                    "instock_text": instock_text,
                })
                print(f"Добавлен товар: {name} ({product_url})")

            except Exception as e:
                print(f"Ошибка при парсинге карточки: {e}")
                # Пропускаем товары, которые не удалось получить
                continue
        
        print(f"Всего спарсено товаров: {len(results)}")
        return results

    except TimeoutException as e:
        # Если страница не загрузилась в течение таймаута, возвращаем пустой список
        print(f"Таймаут при загрузке страницы: {e}")
        print(f"URL: {url}")
        return []
    except WebDriverException as e:
        # Обрабатываем другие ошибки WebDriver
        print(f"Ошибка WebDriver: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        return []
    except Exception as e:
        # Обрабатываем любые другие ошибки
        print(f"Неожиданная ошибка: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        try:
            driver.quit()
        except WebDriverException:
            pass  # Игнорируем ошибки при закрытии драйвера
