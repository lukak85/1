from html.parser import HTMLParser
import codecs
from treelib import Node, Tree


DEBUG_MODE = False

class RoadrunnerHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.html_tokens = []

    def handle_starttag(self, tag, attrs):
        self.html_tokens.append("<" + tag + ">")

    def handle_endtag(self, tag):
        self.html_tokens.append("</" + tag + ">")

    def handle_data(self, data):
        self.html_tokens.append(data)


"""
This is used to extract tags and data and put it into a token list,
from where we'll be able to remove and properly anotate said data
"""

def parse(html_content):
    parser = RoadrunnerHTMLParser()
    parser.feed(html_content)

    # Filter the data that is not neeeded, such as scripts and comments
    return filter_content(parser.html_tokens)
    # return filter_whitespace(parser.html_tokens)

def filter_content(html_list):
    i = 0

    while i < len(html_list):
    
        if html_list[i] == "<script>":
            while html_list[i] != "</script>":
                html_list.pop(i)
            html_list.pop(i)
        
        elif html_list[i] == "<!--":
            while html_list[i] != "-->":
                html_list.pop(i)
            html_list.pop(i)

        elif html_list[i] == "<meta>":
            html_list.pop(i)

        elif html_list[i] == "<head>":
            while html_list[i] != "</head>":
                html_list.pop(i)
            html_list.pop(i)

        # elif html_list[i] == "<img>":
        #     html_list.pop(i)
        # elif html_list[i] == "</img>":
        #     html_list.pop(i)
        
        elif html_list[i] == "<svg>":
            html_list.pop(i)
        elif html_list[i] == "</svg>":
            html_list.pop(i)

        elif html_list[i] == "<br>":
            html_list.pop(i)

        # elif html_list[i] == "<b>":
        #     html_list.pop(i)
        # elif html_list[i] == "</b>":
        #     html_list.pop(i)

        # elif html_list[i] == "<i>":
        #     html_list.pop(i)
        # elif html_list[i] == "</i>":
        #     html_list.pop(i)

        elif html_list[i].isspace():
            html_list.pop(i)

        else:
            i += 1

    return html_list

def filter_whitespace(html_list):
    i = 0

    while i < len(html_list):
        if html_list[i].isspace():
            html_list.pop(i)

        i += 1

    return html_list



"""
Check what matches and properly adjust the expression automatically
"""

def match(site_tokens, sites):
    for site in sites:

        # Which tag/data element we're checking atm
        i = 0

        # Looping trough all HTML elements in the file
        while i < len(site_tokens) and i < len(site):

            # Check for a mismatch in tokens
            if site_tokens[i] != site[i]:

                # Check if it's a tag mismatch or a string mismatch
                if (site_tokens[i][0] == "<" and site_tokens[i][len(site_tokens[i]) - 1] == ">") and (site[i][0] == "<" and site[i][len(site[i]) - 1] == ">"): # Tag mismatch
                    if DEBUG_MODE:
                        print("------------")
                        print("TAG MISMATCH")
                        print("------------")
                        print(site_tokens[i])
                        print(site[i])

                    site_tokens, site, i = tag_mismatch(site_tokens, site, i)

                # There may be no tag mismatch, but just an optional present
                # in site_tokens at this position
                elif site[i][0] == "<" and site[i][len(site[i]) - 1] == ">" and site[i] in site_tokens[i]:
                    True # Here just to skip the next elif statement

                else: # String mismatch
                    if DEBUG_MODE:
                        print("---------------")
                        print("STRING MISMATCH")
                        print("---------------")
                        print(site_tokens[i])
                        print(site[i])

                    site_tokens[i] = "#PCDATA"
                    
            i += 1

    return site_tokens


"""
If a tag missmatch has occured, TODO - napisi do konca lol
"""
def tag_mismatch(site_tokens, site, i):

    # Check terminal tag if it's the end of a list, and depending on what
    # kind of list it is act accordingly
    
    # TODO - fix these methods

    if site_tokens[i] == "</ul>" or site[i] == "</ul>":
        site_tokens, site, i = handle_lists(site_tokens, site, i, "ul", "li")

    elif site_tokens[i] == "</ol>" or site[i] == "</ol>":
        site_tokens, site, i = handle_lists(site_tokens, site, i, "ol", "li")
    
    elif site_tokens[i] == "</tbody>" or site[i] == "</tbody>":
        site_tokens, site, i = handle_lists(site_tokens, site, i, "tbody", "tr")
    
    
    
    # Optional tags

    elif "<" in site[i]:

        found = False

        # Search for optionals on second site
        if "</" not in site[i]: # Making sure it's not an end tag

            # Do a "cross search"
            for j in range(i, min(i + 5, len(site_tokens))):

                if j < len(site) and not found and site[j] == site_tokens[i]:

                    # We found a tag match
                    found = True
                    k = i

                    # We then encapsulate all the stuff inside the tag
                    # into an optional, going to the tag terminator
                    current_start_tag = site[k]
                    current_end_tag = "</" + site[k][1:len(site[k]) - 1] + ">"
                    
                    # If the optional tag includes the tag with the same name
                    # make sure the right one is the closing tag
                    start_tag_depth = 0

                    site[k] = "[" + site[k]
                    site_tokens.insert(k, site[k])
                    k += 1

                    print()
                    print("site_tokens: " + site_tokens[i])
                    print("site: " + site[k])
                    print()

                    # We loop trough the tokens and while we haven't reached
                    # the ending tag, we continue simply adding the tags in
                    while current_end_tag not in site[k] or start_tag_depth != 0:
                        
                        # Increase the nested tag occurence number
                        if site[k] == current_start_tag:
                            start_tag_depth += 1

                        # Decrease the nested tag occurence number
                        elif site[k] == current_end_tag:
                            start_tag_depth -= 1


                        site_tokens.insert(k, site[k])
                        k += 1

                    site[k] = site[k] + "]?"
                    site_tokens.insert(k, site[k])
                    k += 1

                    i = k
                    break
                

    	# If not found ,seach for optionals on wrapper
        if not found:
            for j in range(i, i+5):
                if site[i] == site_tokens[j]:
                    for k in range(i, j):
                        site.insert(k, "[" + site_tokens[k] + "]?")

        # Otherwise assume the optional is on the side of the TODO (??)

    return site_tokens, site, i


def handle_lists(site_tokens, site, i, tag, element_tag):

    # Tag of a list (goofy variable name though, whoops)
    start_tag_li = "<" + tag + ">"
    end_tag_li = "</" + tag + ">"
    
    # Tag of an element of the list
    start_tag_el = "<" + element_tag + ">"
    end_tag_el = "</" + element_tag + ">"

    # In case it's nested (i.e. there's tags with the same name inside
    # this element), check the depth
    tag_depth = 0

    # Check if previous closing tag is the ending tag of a list element
    if end_tag_el in site_tokens[i - 1]:

        # Move back a space
        i -= 1

        # Go back to the very start of the list and be careful about
        # tag depth
        while start_tag_li not in site_tokens[i] or tag_depth != 0:

            if end_tag_li in site_tokens[i]:
                tag_depth += 1
            elif start_tag_li in site_tokens[i]:
                tag_depth -= 1

            i -= 1
        
        # Move forward a space from the start token
        i += 2

        # Start an optional at the beginning of the list element
        site_tokens[i] = "[" + start_tag_el
        
        # Search for the end of said element, similarly as before
        while end_tag_el not in site_tokens[i] or tag_depth != 0:

            if site_tokens[i] == end_tag_li:
                tag_depth += 1
            elif site_tokens[i] == start_tag_li:
                tag_depth -= 1

            i += 1
        
        # End the list element tag
        site_tokens[i] = end_tag_el + "]+"
        i += 1

        # Remove all the other elements of the site
        while end_tag_li not in site_tokens[i]:
            site_tokens.pop(i)

        # Remove all the other elements of the list
        # on the second website
        while end_tag_li not in site[i]:
            site.pop(i)

    return site_tokens, site, i



"""
Run the roadrunner trough apropriate webpages
"""

# Roadrunner testing
#"""
f = codecs.open("../input-extraction/testing/test1.html", 'r')
site1 = parse(f.read())
f = codecs.open("../input-extraction/testing/test2.html", 'r')
site2 = parse(f.read())
#"""

# Roadrunner for overstock.com
"""
f = codecs.open("../input-extraction/overstock.com/jewelry01.html", 'r')
site1 = parse(f.read())
f = codecs.open("../input-extraction/overstock.com/jewelry02.html", 'r')
site2 = parse(f.read())
#"""

# Roadrunner for rtvslo.si
"""
f = codecs.open("../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html", 'r')
site1 = parse(f.read())
f = codecs.open("../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljs╠îe v razredu - RTVSLO.si.html", 'r')
site2 = parse(f.read())
#"""

# Roadrunner for mimovrste.com
"""
f = codecs.open("../input-extraction/mimovrste.com/Entrek pohodne treking palice, karbonske, 3-delne, 66-135 cm, črne _ mimovrste=).html", 'r', encoding="utf8")
site1 = parse(f.read())
f = codecs.open("../input-extraction/mimovrste.com/JBL T600BTNC brezžične slušalke _ mimovrste=).html", 'r', encoding="utf8")
site2 = parse(f.read())
#"""

sites = [site2]
tokens = match(site1, sites)

f = codecs.open("temp.html", 'w')
f.write(''.join(tokens))
f.close()