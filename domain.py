# Extracting domain name

def extract_domain(link):
    split_link = link.split("/")
    return split_link[0] + "//" + split_link[2]