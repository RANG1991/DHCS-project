import csv
import re

all_allowed_stats = [
                "Page size",
                "Total edits",
                "Editors",
                "Pageviews (60 days)",
                "Page watchers",
                "Average time between edits (days)",
                "Average edits per user",
                "Edits made by the top 10% of editors",
                "Links to this page",
                "Links from this page",
                "External links",
                ]

def read_csvs_english_hebrew(file_name_1, file_name_2, weights_dict = {}):
    hebrew_wiki = csv.reader(open(file_name_1, 'r', encoding= "UTF-8"))
    english_wiki = csv.reader(open(file_name_2, 'r', encoding= "UTF-8"))
    dict_of_values_heb = {}
    dict_of_values_en = {}
    hebrew_wiki = [r for r in hebrew_wiki]
    english_wiki = [r for r in english_wiki]
    for i in range(len(hebrew_wiki)):
        if len(hebrew_wiki[i]) > 1 and hebrew_wiki[i][0].startswith("Wikidata"):
            dict_of_values_heb[hebrew_wiki[i][1].split("\n")[0]] = hebrew_wiki[i - 4][0]
    for i in range(len(list(english_wiki))):
        if len(english_wiki[i]) > 1 and english_wiki[i][0].startswith("Wikidata"):
            dict_of_values_en[english_wiki[i][1].split("\n")[0]] = english_wiki[i - 4][0]
    set_values = set(dict_of_values_heb.keys())
    set_values = set_values.intersection(set(dict_of_values_en.keys()))
    values_dict_heb = {}
    values_dict_en = {}
    for row in all_allowed_stats:
        values_dict_heb[row.strip()] = 0
        values_dict_en[row.strip()] = 0
    need_value = False
    for row in hebrew_wiki:
        if len(row) > 1 and row[0].startswith("Wikidata"):
            if row[1].split("\n")[0] in set_values:
                need_value = True
            else:
                need_value = False
        if len(row) > 1 and need_value and row[0].strip() in values_dict_heb.keys():
            values_dict_heb[row[0].strip()] += (int(re.match("\d+", row[1].strip().replace(",", "")).group(0)))
    print(values_dict_heb)
    need_value = False
    for row in english_wiki:
        if len(row) > 1 and row[0].startswith("Wikidata"):
            if row[1].split("\n")[0] in set_values:
                need_value = True
            else:
                need_value = False
        if len(row) > 1 and need_value and row[0].strip() in values_dict_en.keys():
            values_dict_en[row[0].strip()] += (int(re.match("\d+", row[1].strip().replace(",", "")).group(0)))
    print(values_dict_en)
    ratios_dict = {}
    for key in values_dict_en.keys():
        if values_dict_en[key] == 0:
            ratios_dict[key] = 0
            continue
        ratios_dict[key] = (float(values_dict_heb[key]) / values_dict_en[key])
    print(ratios_dict)
    average = 0
    if weights_dict == {}:
        for item in all_allowed_stats:
            weights_dict[item] = 1
    for key in weights_dict.keys():
        average += ratios_dict[key] * weights_dict[key]
    print(average / len(ratios_dict))
    return average / len(ratios_dict)

# read_csvs_english_hebrew(r"C:\Users\Admin\Desktop\dchs_gui\wiki.csv", r"C:\Users\Admin\Desktop\dchs_gui\wiki_en.csv")
# read_csvs_english_hebrew(r"C:\Users\Admin\Desktop\wiki_random.csv", r"C:\Users\Admin\Desktop\wiki_en_random.csv")