# Extracting domain name

def extract_scheme(link):
    return link.split("/")[0]

def extract_domain(link):
    return link.split("/")[2]

def extendRelativePage(page_url, relative_link):
    if not "http:" in relative_link and not "https:" in relative_link:
        if relative_link[0] == "/":
            relative_link = relative_link[1:]

        page_url_split = page_url.split("/")
        if ".html" in page_url_split[len(page_url_split) - 1]:
            page_url = ""

            for url_element in page_url_split[0:len(page_url_split) - 2]:
                page_url += url_element

        else:
            if page_url[len(page_url) - 1] == "/":
                page_url = page_url + relative_link
            else:
                page_url = page_url + "/" + relative_link
    else:
        return relative_link

    return page_url
