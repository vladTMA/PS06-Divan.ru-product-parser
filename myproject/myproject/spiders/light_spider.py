# light_spider.py
import scrapy
from myproject.items import MyprojectItem


class LightSpider(scrapy.Spider):
    name = "light"
    allowed_domains = ["divan.ru"]
    start_urls = ["https://www.divan.ru/category/svet"]

    def parse(self, response):
        # Находим все карточки товаров по семантическому атрибуту
        lamps = response.css('div[itemtype="http://schema.org/Product"]')

        for lamp in lamps:
            item = MyprojectItem()
            item["name"] = lamp.css('[itemprop="name"]::text').get() or "нет данных"
            item["price"] = lamp.css('meta[itemprop="price"]::attr(content)').get() or "нет данных"
            item["currency"] = lamp.css('meta[itemprop="priceCurrency"]::attr(content)').get() or "нет данных"

            # Ссылка: используем urljoin для корректного абсолютного пути
            url = lamp.css('link[itemprop="url"]::attr(href)').get()
            item["url"] = response.urljoin(url) if url else "нет данных"

            item["instock_text"] = lamp.css('div.MainInfo_count__MmnNN::text').get() or "нет данных"
            item["instock_schema"] = lamp.css('link[itemprop="availability"]::attr(href)').get() or "нет данных"

            yield item

