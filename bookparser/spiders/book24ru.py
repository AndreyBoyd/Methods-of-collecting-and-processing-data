import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    # query = 'Гоголь'
    # start_urls = [f'https://book24.ru/search/?q={query}']
    start_urls = ['https://book24.ru/catalog/kosmicheskaya-fantastika-2057/']

    def parse(self, response: HtmlResponse):
        books = response.xpath('//a[contains(@class, "book-preview__title-link")]/@href').extract()
        for book in books:
            yield response.follow(book, callback=self.book_parse)

        next_page = response.xpath('//a[@class="catalog-pagination__item _text js-pagination-catalog-item" and text()="Далее"]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        book_link = response.url
        book_name = response.xpath("//h1/text()").extract_first()
        book_authors = response.xpath('//span[@class="item-tab__chars-key" and text()="Автор:"]/../span[@class="item-tab__chars-value"]/a/text()').extract_first()
        book_old_price = response.xpath("//div[@class='item-actions__price-old']/text()").extract()
        book_new_price = response.xpath("//div[@class='item-actions__price']/b/text()").extract()
        book_rating = response.xpath("//span[@class='rating__rate-value']/text()").extract()

        yield BookparserItem(book_link=book_link, book_name=book_name, book_authors=book_authors,
                             book_old_price=book_old_price, book_new_price=book_new_price, book_rating=book_rating)

