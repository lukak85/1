# Extracting domain name

def extract_scheme(link):
    return link.split("/")[0]

def extract_domain(link):
    return link.split("/")[2]