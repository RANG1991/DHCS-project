import time
from lxml import html
import requests
from requests.compat import urljoin, quote, unquote
import csv

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

base = "https://he.wikipedia.org/"
base_en = "https://en.wikipedia.org/"
base_and_wiki = "https://he.wikipedia.org/wiki/"
start_url = "https://he.wikipedia.org/wiki/פורטל:ישראל"
start_url_random = "https://he.wikipedia.org/wiki/Special:Random"
IS_RANDOM = False

def find_first_regular():
    response = requests.get(start_url)
    tree = html.fromstring(response.content)
    links = tree.xpath("//div[@class=\"plainlinks\" and contains(., \"ערכים מומלצים\")]/following-sibling::*[1]//a/@href")
    for i in range(1, 6):
        # print(unquote(links[i]).replace("/wiki/", ""))
        next_page = urljoin(base, links[i])
        parse_single_page(next_page)
        if i % 10 == 0:
            time.sleep(2)

def find_first_random():
    global IS_RANDOM
    IS_RANDOM = True
    for i in range(5):
        parse_single_page(start_url_random)
        if i % 10 == 0:
            time.sleep(2)

def parse_single_page(url):
    print("now I'm parsing :" + str(url))
    response = requests.get(url)
    tree = html.fromstring(response.content)
    link = tree.xpath("//a[contains(.,\"גרסאות קודמות\")]/@href")[0]
    link = urljoin(base, link)
    l = tree.xpath("//li[starts-with(@class, \"interlanguage-link interwiki-en\")]/a/@href")
    if len(l) == 0:
        print("can't parse this url: " + str(unquote(url)[url.index("wiki/") + 5:]))
        return
    english_page = l[0]
    english_page = urljoin(base_en, english_page)
    parse_history_versions(link)
    parse_single_page_english(english_page)

def parse_history_versions(url):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    link = tree.xpath("//a[contains(.,\"סטטיסטיקת גרסאות קודמות\")]/@href")[0]
    parse_stats(link)

def parse_stats(url):
    if IS_RANDOM:
        f = open("wiki_random.csv", "a+", encoding="UTF-8")
    else:
        f = open("wiki.csv", "a+", encoding="UTF-8")
    csv_file = csv.writer(f, delimiter=',', quotechar='\"')
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    header = tree.xpath("//header[@class=\"panel-heading\"]//a[starts-with(@href, 'https://he.wikipedia.org')]/text()")
    csv_file.writerow(header)
    all_table_rows_selector = tree.xpath("//tr")
    for row_selector in all_table_rows_selector:
        row_array = row_selector.xpath(".//td//text()")
        row_array = [r.strip() for r in row_array]
        row_array = [r for r in row_array if r != ""]
        csv_file.writerow(row_array)

def parse_single_page_english(url):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    next_page = tree.xpath("//a[contains(.,\"View history\")]/@href")[0]
    next_page = urljoin(base_en, next_page)
    parse_history_versions_english_page(next_page)

def parse_history_versions_english_page(url):
     response = requests.get(url)
     tree = html.fromstring(response.content)
     next_page = tree.xpath("//a[contains(.,\"Page statistics\")]/@href")[0]
     parse_stats_english_page(next_page)

def parse_stats_english_page(url):
    if IS_RANDOM:
        f = open("wiki_en_random.csv", "a+", encoding="UTF-8")
    else:
        f = open("wiki_en.csv", "a+", encoding="UTF-8")
    csv_file = csv.writer(f, delimiter=',', quotechar='\"')
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    header = tree.xpath("//header[@class=\"panel-heading\"]//a[starts-with(@href, 'https://en.wikipedia.org')]/text()")
    csv_file.writerow(header)
    all_table_rows_selector = tree.xpath("//tr")
    for row_selector in all_table_rows_selector:
        row_array = row_selector.xpath(".//td//text()")
        row_array = [r.strip() for r in row_array]
        row_array = [r for r in row_array if r != ""]
        csv_file.writerow(row_array)

def parser_multiple_links_from_file(file_name, is_random = False):
    if is_random:
        global IS_RANDOM
        IS_RANDOM = True
    f = open(file_name, "r", encoding="UTF-8")
    i = 0
    for row in f:
        parse_single_page(urljoin(base_and_wiki, quote(row.strip())))
        i += 1
        if i % 10 == 0:
            time.sleep(2)

# parser_multiple_links_from_file(r"C:\Users\Admin\Desktop\out_articales_porn.txt", is_random=False)
# find_first_random()