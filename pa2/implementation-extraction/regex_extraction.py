import re
import json

# output = extracted data in JSON format
# extracted using a single regex
def extract_overstock(html_content):
    # od 280. vrstice naprej je prvi artikel
    data = []

    title = """<td\s+valign=\"top\">\s+<a\s+href=\"\S*\"><b>(.*)</b>"""
    listPrice =  """<b>List\sPrice:<\/b><\/td><td\salign=\"left\"\s+nowrap=\"nowrap\"><s>(.*)</s></td>"""
    price = """<td\salign=\"left\"\snowrap=\"nowrap\"><span\sclass=\"bigred\"><b>(.*)</b></span>"""
    saving = """<td\salign=\"left\"\snowrap=\"nowrap\"><span\sclass=\"littleorange\">(\$[0-9\.,]*).*</span></td>"""
    savingPercent = """<td\salign=\"left\"\snowrap=\"nowrap\"><span\sclass=\"littleorange\">.*\((.*)\)</span></td>"""
    content = """<td\svalign=\"top\"><span\s+class=\"normal\">([\s\S]*?)<br>"""

    titles = list(re.finditer(title, html_content))
    listPrices = list(re.finditer(listPrice, html_content))
    prices = list(re.finditer(price, html_content))
    savings = list(re.finditer(saving, html_content))
    savingPercents = list(re.finditer(savingPercent, html_content))
    contents = list(re.finditer(content, html_content))

    # prices = removeTags(prices)
    # print(listPrices[1].group(1))

    if len(titles) == len(listPrices) == len(prices) == len(savings) == len(savingPercents) == len(contents):
        for i in range(len(titles)):
            cont = contents[i].group(1).replace('\n', ' ')
            data.append({
                "Title": titles[i].group(1),
                "ListPrice": listPrices[i].group(1),
                "Price": prices[i].group(1),
                "Saving": savings[i].group(1),
                "SavingPercent": savingPercents[i].group(1),
                "Content": cont
            })
    # print(data)

    print(json.dumps(data, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))

    # po 15 jih je
    #<b>List Price:</b></td><td align="left" nowrap="nowrap"><s>$149.00</s></td>
    #<td align="left" nowrap="nowrap"><span class="bigred"><b>$69.99</b></span>
    #<td align="left" nowrap="nowrap"><span class="littleorange">$79.01 (53%)</span></td>
    #<td valign="top"><span class="normal">This ladies fashion ring dazzles
    # <td align="left" nowrap="nowrap"><span class="bigred"><b>$69.99</b></span>



def extract_rtvslo(html_content):
    data = []
    # <div class="author-timestamp"> \n <strong>Miha Merljak</strong>
    # <div class="publish-meta"> \n 28. december 2018 ob 08:51<br> Ljubljana		 - 		MMC RTV SLO			</div>
    # <meta name="title" content="Audi A6 50 TDI quattro: nemir v premijskem razredu">
    # <div class="subtitle">Test nove generacije</div>
    # <p class="lead">To je novi audi A6. V razred najdražjih in najbolj premijskih žrebcev je vnesel nemir, še preden je sploh zapeljal na parkirni prostor, rezerviran za izvršnega direktorja. </p> </header>
    # 1024 vrstica - <p class="Body"></p><p class="Body">

    author = """<div\s+class=\"author-timestamp\">\s+<strong>(.*)</strong>"""
    publishedTime = """<div\s+class=\"publish-meta\">\s+(.*)<br>"""
    title = """<meta\sname=\"title\"\s+content=\"(.*)\">"""
    subtitle = """<div\s+class=\"subtitle\">(.*)</div>"""
    lead = """<p\s+class=\"lead\">(.*)</p>"""
    content = """<\/div>[\s]*<\/figure>[\s]*<p([\s\S]*?)(?=(<figure class=\"mceNonEditable)|(<div class=\"gallery\">))"""

    authorD = re.findall(author, html_content)
    publishedTimeD = re.findall(publishedTime, html_content)
    titleD = re.findall(title, html_content)
    subtitleD = re.findall(subtitle, html_content)
    leadD = re.findall(lead, html_content)
    contentD = re.findall(content, html_content)

    contentD = removeTags(contentD)

    # v stringe
    authorD = ' '.join(authorD)
    publishedTimeD = ' '.join(publishedTimeD)
    titleD = ' '.join(titleD)
    subtitleD = ' '.join(subtitleD)
    leadD = ' '.join(leadD)
    contentD = ''.join(str(e) for e in contentD)
    # print(type(contentD))

    data.append({"Author": authorD, "PublishedTime": publishedTimeD, "Title": titleD, "Subtitle": subtitleD, "Lead": leadD, "Content": contentD})
    # print(data)
    print(json.dumps(data, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


def removeTags(text):
    # re library
    # clean = re.compile('<.*?>')
    # return re.sub(clean, '', text)
    clean = re.compile('<.*?>')
    nov = (' '.join(str(e) for e in text))
    nov = re.sub(clean, '', nov)
    nov = nov.replace('\\n', ' ')
    nov = nov.replace('\\t', '')
    nov = nov.replace('class="Body">', '')
    nov = nov.replace('>', '')
    nov = nov.replace('<figure class="mceNonEditable', '')
    return nov

def extract_mimovrste(html_content):
    data = []

    title = """<title>(.*)\|\s+(?=mimovrste=\)</title>)"""
    price = """price__wrap__box__final\">\n*(.*)€"""
    ratingPercent = """class=\"badge-rating__percent\">\\n(.*)"""
    number = """<span data-sel=\"catalog-number\">(.*)</span></span>"""
    reviewNumber = """data-testid=\"badge-rating-count\">\\n(.*)\s+ocen"""

    titleD = re.findall(title, html_content)
    priceD = re.findall(price, html_content)
    ratingPercentD = re.findall(ratingPercent, html_content)
    numberD = re.findall(number, html_content)
    reviewNumberD = re.findall(reviewNumber, html_content)
    # print(reviewNumberD)
    # print(priceD)

    titleD = ' '.join(titleD)
    priceD = ' '.join(priceD)
    ratingPercentD = ' '.join(ratingPercentD)
    numberD = ' '.join(numberD)
    reviewNumberD = ' '.join(reviewNumberD)

    priceD = priceD.replace(' ', '')
    priceD = priceD + "€"
    ratingPercentD = ratingPercentD.replace(' ', '')
    reviewNumberD = reviewNumberD.replace(' ', '')

    data.append({"Title": titleD, "Price": priceD, "RatingPercent": ratingPercentD, "Number":  numberD, "ReviewNumber": reviewNumberD})
    # print(data)
    print(json.dumps(data, indent=3, sort_keys=False, separators=(', ', ' : '), ensure_ascii=False))


def runRegex():

    # RTV SLO
    print()
    print("---------------------------------------------------------------------")
    print("Extracting data with Regex from rtvslo.si")
    print("---------------------------------------------------------------------")
    print("* * * * * 1st rtvslo.si page * * * * *")
    f = open("../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html", "r")
    a = f.read()
    extract_rtvslo(a)
    f.close()
    #
    print("* * * * * 2nd rtvslo.si page * * * * *")
    ff = open("../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", "r")
    aa = ff.read()
    extract_rtvslo(aa)
    ff.close()

    # OVERSTOCK
    print()
    print("---------------------------------------------------------------------")
    print("Extracting data with Regex from overstock.com")
    print("---------------------------------------------------------------------")
    print("* * * * * 1st overstock.com page * * * * *")
    g = open("../input-extraction/overstock.com/jewelry01.html", 'r', encoding='latin')
    b = g.read()
    extract_overstock(b)
    g.close()
    print("* * * * * 2nd overstock.com page * * * * *")
    gg = open("../input-extraction/overstock.com/jewelry02.html", "r", encoding="latin-1")
    bb = gg.read()
    extract_overstock(bb)
    gg.close()

    # MIMOVRSTE
    print()
    print("---------------------------------------------------------------------")
    print("Extracting data with Regex from mimovrste.com")
    print("---------------------------------------------------------------------")

    print("* * * * * 1st mimovrste.com page * * * * *")
    h = open("../input-extraction/mimovrste.com/Entrek pohodne treking palice, karbonske, 3-delne, 66-135 cm, črne _ mimovrste=).html", "r")
    c = h.read()
    extract_mimovrste(c)
    h.close()

    print("* * * * * 2nd mimovrste.com page * * * * *")
    i = open("../input-extraction/mimovrste.com/JBL T600BTNC brezžične slušalke _ mimovrste=).html", "r")
    cc = i.read()
    extract_mimovrste(cc)
    i.close()
