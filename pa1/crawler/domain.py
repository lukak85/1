# Extracting domain name

def extract_scheme(link):
    return link.split("/")[0]

def extract_domain(link):
    return link.split("/")[2]

def extendRelativePage(page_url, relative_link):

    if len(relative_link) >= 1 and relative_link[0] == "#":
        return page_url
    elif len(relative_link) >= 2 and relative_link[0] == "/" and relative_link[1] == "#":
        return page_url
    elif not "http:" in relative_link and not "https:" in relative_link:

        if relative_link[0] == "/":
            relative_link = relative_link[1:]

        page_url_split = page_url.split("/")
        
        if len(page_url_split) > 3 and "." in page_url_split[len(page_url_split) - 1]:
            page_url = ""

            for url_element in page_url_split[:len(page_url_split) - 1]:
                page_url = page_url + url_element + "/"

        else:
            if page_url[len(page_url) - 1] == "/":
                page_url = page_url + relative_link
            else:
                page_url = page_url + "/" + relative_link

    else:
        page_url = relative_link

    return page_url
