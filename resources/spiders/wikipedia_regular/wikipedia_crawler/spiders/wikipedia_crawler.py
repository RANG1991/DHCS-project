#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
import operator
import csv
import requests
from time import sleep

next_pages_set = set()

class QuotesSpider(scrapy.Spider):
    name = "wikipedia"
    start_urls = [
        'https://he.wikipedia.org/wiki/פורטל:ישראל',
    ]
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

    def parse(self, response):
        links = response.xpath("//div[@class=\"plainlinks\" and contains(., \"ערכים מומלצים\")]/following-sibling::*[1]//a/@href")
        links = links[151:]
        for link in links:
            next_page = response.urljoin(link.extract())
            request = scrapy.Request(next_page, callback=self.parse_single_page)
            yield request

    def parse_single_page(self, response):
        next_page = response.xpath("//a[contains(.,\"גרסאות קודמות\")]/@href")
        next_page = response.urljoin(next_page.extract_first())
        english_page = response.xpath("//li[@class=\"interlanguage-link interwiki-en\"]/a/@href")
        english_page = response.urljoin(english_page.extract_first())
        # if next_page not in next_pages_set:
        #     next_pages_set.add(next_page)
        request = response.follow(next_page, callback=self.parse_history_versions)
        yield request
        # if english_page not in next_pages_set:
        #     next_pages_set.add(english_page)
        request = response.follow(english_page, callback=self.parse_single_page_english)
        yield request

    def parse_history_versions(self, response):
        next_page = response.xpath("//a[contains(.,\"סטטיסטיקת גרסאות קודמות\")]/@href")
        next_page = response.urljoin(next_page.extract_first())
        if next_page not in next_pages_set:
            next_pages_set.add(next_page)
            yield scrapy.Request(next_page, callback=self.parse_stats)

    def parse_stats(self, response):
        f = open("wiki.csv", "a+", encoding="UTF-16")
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
            request = response.follow(next_page, callback=self.parse_history_versions_english_page)
            yield request

    def parse_history_versions_english_page(self, response):
        next_page = response.xpath("//a[contains(.,\"Page statistics\")]/@href")
        next_page = response.urljoin(next_page.extract_first())
        if next_page not in next_pages_set:
            next_pages_set.add(next_page)
            yield scrapy.Request(next_page, callback=self.parse_stats_english_page)

    def parse_stats_english_page(self, response):
        f = open("wiki_en.csv", "a+", encoding="UTF-16")
        csv_file = csv.writer(f, delimiter=',', quotechar='\"')
        header = response.xpath("//header[@class=\"panel-heading\"]//a[starts-with(@href, 'https://en.wikipedia.org')]").xpath("string()").extract_first()
        csv_file.writerow([header])
        all_table_rows_selector = response.xpath("//tr")
        for row_selector in all_table_rows_selector:
            row_array = row_selector.xpath(".//td").xpath("string()").extract()
            row_array = [r.strip() for r in row_array]
            csv_file.writerow(row_array)