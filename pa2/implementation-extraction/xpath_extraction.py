import json
import pickle
import re
from lxml import html

"""
     RTVSLO data extraction.
"""


def extract_rtvslo_with_xpath(filename, output):
    # one data record per sample page

    html_content = open(filename, 'r', encoding="utf-8").read()
    html_content = html.fromstring(html_content)
    # print(html_content)
    # print(et.tostring(html_content, pretty_print=True).decode("utf-8"))

    # data to be extracted - author, publish_time, title, subtitle, lead, content
    # xpath expressions
    author = '//*[@class="author-name"]/text()'
    publish_time = '//*[@class="publish-meta"]/text()'
    title = '//*[@id="main-container"]/div[3]/div/header/h1/text()'
    subtitle = '//*[@class="subtitle"]/text()'
    lead = '//*[@class="lead"]/text()'
    content = '//*[@class="article-body"]/article/p/text()|//*[@class="article-body"]/article/p/strong/text()'

    # extract data with xpath
    rtvslo_author = html_content.xpath(author)
    rtvslo_publish_time = html_content.xpath(publish_time)
    rtvslo_title = html_content.xpath(title)
    rtvslo_subtitle = html_content.xpath(subtitle)
    rtvslo_lead = html_content.xpath(lead)
    rtvslo_content = html_content.xpath(content)

    # check values
    # print(rtvslo_author[0])
    # print(rtvslo_publish_time[0])
    # print(rtvslo_title[0])
    # print(rtvslo_subtitle[0])
    # print(rtvslo_lead[0])
    # print(rtvslo_content)

    # post processing of extracted values where needed
    rtvslo_publish_time_1 = rtvslo_publish_time[0].__str__()
    rtvslo_publish_time_1 = re.sub(r'(\n\t\t)', r'', rtvslo_publish_time_1)

    rtvslo_content_1 = ''
    for content in rtvslo_content:
        rtvslo_content_1 = rtvslo_content_1 + content.__str__() + " "

    # dictionary with extracted values
    rtvslo_xpath_dictionary = {
        "Author": rtvslo_author[0],
        "PublishTime": rtvslo_publish_time_1,
        "Title": rtvslo_title[0],
        "Subtitle": rtvslo_subtitle[0],
        "Lead": rtvslo_lead[0],
        "Content": rtvslo_content_1
    }

    # save to output file
    with open("../output-extraction/xpath/" + output, 'w') as json_file:
        json.dump(rtvslo_xpath_dictionary, json_file, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False)

    # pretty-printing json
    print(json.dumps(rtvslo_xpath_dictionary, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


"""
    OVERSTOCK data extraction.
"""


def extract_overstock_with_xpath(filename, output):
    # a list of data records

    html_content_overstock = open(filename, 'r', encoding="latin-1").read()
    html_content_overstock = html.fromstring(html_content_overstock)
    # print(html_content_overstock)
    # print(et.tostring(html_content_overstock, pretty_print=True).decode("latin-1"))

    # data (lists) - title, list price, price, saving, saving percent, content
    title = '//*/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/a/b/text()'
    list_price = '//*/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]' + \
                 '/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text()'
    price = '//*/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]' + \
            '/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text()'
    saving = '//*/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]' + \
             '/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()'
    saving_percent = '//*/body/table[2]/tbody/tr[1]/td[5]/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]' + \
                     '/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text()'
    content = '//*/span[@class="normal"]/text()|//*/span[@class="normal"]/a/span/b/text()'

    overstock_titles = html_content_overstock.xpath(title)
    overstock_list_prices = html_content_overstock.xpath(list_price)
    overstock_prices = html_content_overstock.xpath(price)
    overstock_savings = html_content_overstock.xpath(saving)
    overstock_content = html_content_overstock.xpath(content)

    # check values
    # print(overstock_titles)
    # print(overstock_list_prices )
    # print(overstock_prices)
    # print(overstock_savings)
    # print(overstock_content)

    # output will be a list of data records
    overstock_xpath_dictionary_data = []
    number_of_records = len(overstock_titles)
    for i in range(number_of_records):
        overstock_title = overstock_titles[i]
        overstock_list_price = overstock_list_prices[i]
        overstock_price = overstock_prices[i]
        overstock_saving = overstock_savings[i]
        overstock_content_1 = overstock_content[2*i]
        overstock_content_link = overstock_content[2*i+1]

        # some extra processing where needed
        overstock_saving = overstock_saving.split(" ", 1)
        overstock_saving_n = overstock_saving[0]
        overstock_saving_p = overstock_saving[1]

        overstock_content_1 = overstock_content_1.replace("\n", " ") + " " + overstock_content_link

        # saving data to dictionary
        overstock_xpath_dictionary = {
            "Title": overstock_title,
            "Content": overstock_content_1,
            "ListPrice": overstock_list_price,
            "Price": overstock_price,
            "Saving": overstock_saving_n,
            "SavingPercent": overstock_saving_p
        }

        # append to the list
        overstock_xpath_dictionary_data.append(overstock_xpath_dictionary)

    #  save to output folder
    with open("../output-extraction/xpath/" + output, 'w') as json_file:
        json.dump(overstock_xpath_dictionary_data, json_file, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False)


    # pretty-printing json
    print(json.dumps(overstock_xpath_dictionary_data, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


"""
    MIMOVRSTE data extraction.
"""


def extract_mimovrste_with_xpath(filename, output):
    html_content_mimovrste = open(filename, 'r', encoding="utf-8").read()
    html_content_mimovrste = html.fromstring(html_content_mimovrste)
    # print(html_content_overstock)
    # print(et.tostring(html_content_mimovrste, pretty_print=True).decode("utf-8"))

    # data to be extracted - title, price, item number, number of reviews, rating percents
    title = '//*[@id="main-content"]/div/div/div[2]/article/h1/text()'
    price = '//*[@class="price__wrap__box__final"]/text()'
    item_number = '//*[@class="additional-info__warranty-and-catalog-number"]/span/span/text()'
    number_of_reviews = '//*[@class="reviews__ratings"]/h2/text()'
    rating_p = '//*[@class="product-ratings__overall"]/span/text()'

    mimovrste_title = html_content_mimovrste.xpath(title)
    mimovrste_price = html_content_mimovrste.xpath(price)
    mimovrste_item_number = html_content_mimovrste.xpath(item_number)
    mimovrste_number_of_reviews = html_content_mimovrste.xpath(number_of_reviews)
    mimovrste_rating_p = html_content_mimovrste.xpath(rating_p)

    # check values
    # print(mimovrste_title)
    # print(mimovrste_price)
    # print(mimovrste_item_number)
    # print(mimovrste_number_of_reviews)
    # print(mimovrste_rating_p)

    # some extra post processing where needed
    mimovrste_title = mimovrste_title[0].strip()
    mimovrste_price = mimovrste_price[0].strip()
    mimovrste_item_number = mimovrste_item_number[0].strip()
    mimovrste_number_of_reviews = mimovrste_number_of_reviews[0].strip()
    mimovrste_number_of_reviews = mimovrste_number_of_reviews[7:9]
    mimovrste_rating_p = mimovrste_rating_p[0].strip()

    mimovrste_xpath_dictionary = {
        "Title": mimovrste_title,
        "Price": mimovrste_price,
        "Number": mimovrste_item_number,
        "ReviewNumber": mimovrste_number_of_reviews,
        "RatingPercent": mimovrste_rating_p
    }

    #  save to output folder
    with open("../output-extraction/xpath/" + output, 'w') as json_file:
        json.dump(mimovrste_xpath_dictionary, json_file, indent=3, sort_keys=False, separators=(', ', ' : '),
                  ensure_ascii=False)

    # pretty-printing json
    print(json.dumps(mimovrste_xpath_dictionary, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


def run_xpath():
    # rtvslo.si
    print()
    print("---------------------------------------------------------------------")
    print("Extracting data with XPath from rtvslo.si")
    print("---------------------------------------------------------------------")

    rtvslo1_filename = "../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html"
    print()
    print("* * * * * 1st rtvslo.si page * * * * *")
    print()
    extract_rtvslo_with_xpath(rtvslo1_filename, "rtvslo1.json")

    rtvslo2_filename = "../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html"
    print()
    print("* * * * * 2nd rtvslo.si page * * * * *")
    print()
    extract_rtvslo_with_xpath(rtvslo2_filename, "rtvslo2.json")

    # overstock.com
    print()
    print("---------------------------------------------------------------------")
    print("Extracting data with XPath from overstock.com")
    print("---------------------------------------------------------------------")

    overstock1_filename = "../input-extraction/overstock.com/jewelry01.html"
    print()
    print("* * * * * 1st overstock.com page * * * * *")
    print()
    extract_overstock_with_xpath(overstock1_filename, "overstock1.json")

    overstock2_filename = "../input-extraction/overstock.com/jewelry02.html"
    print()
    print("* * * * * 2nd overstock.com page * * * * *")
    print()
    extract_overstock_with_xpath(overstock2_filename, "overstock2.json")

    # mimovrste.com
    print()
    print("---------------------------------------------------------------------")
    print("Extracting data with XPath from mimovrste.com")
    print("---------------------------------------------------------------------")

    mimovrste1_filename = "../input-extraction/mimovrste.com/Entrek pohodne treking palice, karbonske, 3-delne, 66-135 cm, črne _ mimovrste=).html"
    print()
    print("* * * * * 1st mimovrste.com page * * * * *")
    print()
    extract_mimovrste_with_xpath(mimovrste1_filename, "mimovrste1.json")

    mimovrste2_filename = "../input-extraction/mimovrste.com/JBL T600BTNC brezžične slušalke _ mimovrste=).html"
    print()
    print("* * * * * 2nd mimovrste.com page * * * * *")
    print()
    extract_mimovrste_with_xpath(mimovrste2_filename, "mimovrste2.json")
