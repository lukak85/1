import re
import json

# output = extracted data in JSON format
# extracted using a single regex
def extract_overstock(html_content):
    # od 280. vrstice naprej je prvi artikel
    data = []

    # po 15 jih je
    #<b>List Price:</b></td><td align="left" nowrap="nowrap"><s>$149.00</s></td>
    #<td align="left" nowrap="nowrap"><span class="bigred"><b>$69.99</b></span>
    #<td align="left" nowrap="nowrap"><span class="littleorange">$79.01 (53%)</span></td>
    #<td valign="top"><span class="normal">This ladies fashion ring dazzles
    # <td align="left" nowrap="nowrap"><span class="bigred"><b>$69.99</b></span>
    regex = {
        "Title": "<td\svalign=\"top\">\s+<a\s+href=\"\S*\"><b>(.*)</b>",
        "ListPrice": "<b>List\sPrice:<\/b><\/td><td\salign=\"left\"\s+nowrap=\"nowrap\"><s>(.*)</s></td>",
        "Price": "<td\salign=\"left\"\snowrap=\"nowrap\"><span\sclass=\"bigred\"><b>(.*)</b></span>",
        "Saving": "<td\salign=\"left\"\snowrap=\"nowrap\"><span\sclass=\"littleorange\">(\$[0-9\.,]*).*</span></td>",
        "SavingPercent": "<td\salign=\"left\"\snowrap=\"nowrap\"><span\sclass=\"littleorange\">.*\((.*)\)</span></td>",
        "Content": "<td\svalign=\"top\"><span\s+class=\"normal\">([\s\S]*?)<br>"
    }


def extract_rtvslo(html_content):
    data = []

    # <div class="author-timestamp"> \n <strong>Miha Merljak</strong>
    # <div class="publish-meta"> \n 28. december 2018 ob 08:51<br> Ljubljana		 - 		MMC RTV SLO			</div>
    # <meta name="title" content="Audi A6 50 TDI quattro: nemir v premijskem razredu">
    # <div class="subtitle">Test nove generacije</div>
    # <p class="lead">To je novi audi A6. V razred najdražjih in najbolj premijskih žrebcev je vnesel nemir, še preden je sploh zapeljal na parkirni prostor, rezerviran za izvršnega direktorja. </p> </header>
    regex = {
        "Author": "<div\s+class=\"author-timestamp\">\s+<strong>(.*)</strong>",
        "PublishedTime": "<div\s+class=\"publish-meta\">\s+(.*)<br>",
        "Title": "<meta\sname=\"title\"\s+content=\"(.*)\">",
        "SubTitle": "<div\s+class=\"subtitle\">(.*)</div>",
        "Lead": "<p\s+class=\"lead\">(.*)</p>",
        "Content": ""
    }

def extract_mimovrste(html_content):
    data = []


if __name__ == "__main__":
    pass
