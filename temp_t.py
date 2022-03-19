#!/usr/bin/env python3

# URL canonization
from urllib.parse import urlparse
from urllib.parse import urlsplit

# testing urls
url1 = "http://www.cs.indiana.edu" # add trailing slash -> http://cs.indiana.edu/
url2 = "http://cs.indiana.edu:80/" # remove default port number -> http://cs.indiana.edu/
url3 = "http://cs.indiana.edu/People" # add trailing slash -> http://cs.indiana.edu/People/
url4 = "http://cs.indiana.edu/path#anchor" # remove anchor / fragment -> http://cs.indiana.edu/path/
url5 = "http://cs.indiana.edu:80/index.html"
url6 = "http://cs.indiana.edu:80/test/./../end" # remove unnecessary path parts -> http://cs.indiana.edu/end/
url7 = "/relative/path" # relative to absolute path - mors poznat absolute? domain?
url8 = "http://cs.indiana.edu/file.pdf" # remove -> http://cs.indiana.edu/
url9 = "http://cs.indiana.edu:80/My File.html" # encode disallowed characters -> http://cs.indiana.edu:80/My%20File.html
url10 = "http://CS.INDIANA.EDU/path" # upper case to lower case -> http://cs.indiana.edu/path/


def urlCanonization(url, parent_scheme, parent_netloc):
    print(url)

    parsed_url = []
    parsed_url = urlparse(url, allow_fragments=True)
    print(parsed_url)

    scheme = parsed_url.scheme
    # relative to absolute
    if (scheme == ""):
        scheme = parent_scheme
    scheme = scheme + ("://")

    netloc = parsed_url.netloc
    # relative to absolute
    if (netloc == ""):
        netloc = parent_netloc
    netloc = netloc.lower()
    # removing port number
    netloc = parsed_url.hostname
    # removing www - if not removed beforehand
    if (netloc[0] == "w" and netloc[1] == "w" and netloc[2] == "w"):
        netloc = netloc[4:]

    path = parsed_url.path
    # no path
    if (path == ""):
        netloc = netloc + "/"

    # removing default filename

    params = parsed_url.params
    query = parsed_url.query
    fragment = parsed_url.fragment
    print(scheme + netloc + path + params)





    return url


urlCanonization(url3, "", "")