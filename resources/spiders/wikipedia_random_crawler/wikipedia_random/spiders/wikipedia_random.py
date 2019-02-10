#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import operator
import csv
import requests
from urllib.parse import quote, urljoin

next_pages_set = set()
i = 0

urls = []
for i in range(1, 11):
    urls.append("https://he.wikipedia.org/wiki/Special:Random")

class QuotesSpider(scrapy.Spider):
    name = "wikipedia_random"
    start_urls = urls
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

    # def parse(self, response):
    #     link = response.xpath("//a[contains(.,\"ערך אקראי\")]/@href")
    #     next_page = response.urljoin(link.extract_first())
    #     yield scrapy.Request(next_page, callback=self.parse_helper, dont_filter=True)
    #
    # def parse_helper(self, response):
    #     link = response.xpath("//a[contains(.,\"ערך אקראי\")]/@href")
    #     next_page = response.urljoin(link.extract_first())
    #     request = scrapy.Request(next_page, callback=self.parse_single_page)
    #     yield request
    #     global i
    #     i += 1
    #     if i <= 10:
    #         print(i)
    #         request = scrapy.Request(next_page, callback=self.parse_helper, dont_filter=True)
    #         yield request

    def parse(self, response):
        next_page = response.xpath("//a[contains(.,\"גרסאות קודמות\")]/@href")
        next_page = response.urljoin(next_page.extract_first())
        english_page = response.xpath("//li[@class=\"interlanguage-link interwiki-en\"]/a/@href")
        english_page = response.urljoin(english_page.extract_first())
        # if next_page not in next_pages_set:
        #     next_pages_set.add(next_page)
        request = response.follow(next_page, callback=self.parse_history_versions, dont_filter=True)
        yield request
        # if english_page not in next_pages_set:
        #     next_pages_set.add(english_page)
        request = response.follow(english_page, callback=self.parse_single_page_english, dont_filter=True)
        yield request

    def parse_history_versions(self, response):
        next_page = response.xpath("//a[contains(.,\"סטטיסטיקת גרסאות קודמות\")]/@href")
        next_page = response.urljoin(next_page.extract_first())
        if next_page not in next_pages_set:
            next_pages_set.add(next_page)
            yield scrapy.Request(next_page, callback=self.parse_stats, dont_filter=True)

    def parse_stats(self, response):
        f = open("wiki_random.csv", "a+", encoding="UTF-16")
        csv_file = csv.writer(f, delimiter=',', quotechar='\"')
        header = response.xpath("//header[@class=\"panel-heading\"]//a[starts-with(@href, 'https://he.wikipedia.org')]").xpath("string()").extract_first()
        csv_file.writerow([header])
        all_table_rows_selector = response.xpath("//tr")
        for row_selector in all_table_rows_selector:
            row_array = row_selector.xpath(".//td").xpath("string()").extract()
            row_array = [r.strip() for r in row_array]
            csv_file.writerow(row_array)

    def parse_single_page_english(self, response):
        next_page = response.xpath("//a[contains(.,\"View history\")]/@href")
        next_page = response.urljoin(next_page.extract_first())
        if next_page not in next_pages_set:
            next_pages_set.add(next_page)
            request = response.follow(next_page, callback=self.parse_history_versions_english_page, dont_filter=True)
            yield request

    def parse_history_versions_english_page(self, response):
        next_page = response.xpath("//a[contains(.,\"Page statistics\")]/@href")
        next_page = response.urljoin(next_page.extract_first())
        if next_page not in next_pages_set:
            next_pages_set.add(next_page)
            yield scrapy.Request(next_page, callback=self.parse_stats_english_page, dont_filter=True)

    def parse_stats_english_page(self, response):
        f = open("wiki_en_random.csv", "a+", encoding="UTF-16")
        csv_file = csv.writer(f, delimiter=',', quotechar='\"')
        header = response.xpath("//header[@class=\"panel-heading\"]//a[starts-with(@href, 'https://en.wikipedia.org')]").xpath("string()").extract_first()
        csv_file.writerow([header])
        all_table_rows_selector = response.xpath("//tr")
        for row_selector in all_table_rows_selector:
            row_array = row_selector.xpath(".//td").xpath("string()").extract()
            row_array = [r.strip() for r in row_array]
            csv_file.writerow(row_array)
