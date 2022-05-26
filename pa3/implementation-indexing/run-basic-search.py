from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup

import os
import sys
import time
import string
from stopwords import stop_words_slovene

DEBUG_MODE = False
MAX_SNIPPET = 3



arguments = [argument.lower() for argument in sys.argv[1:]]
pages = []

start_time = time.time()

for root, _, files in os.walk("../data"):

    for file in files:

         if file.endswith(".html"):
            f = open(os.path.join(root, file), 'r', encoding="utf8")
            
            current_path = os.path.join(root, file).replace("../data", "")

            current_page = BeautifulSoup(f.read(), 'lxml')

            if DEBUG_MODE:
                print("----------------------------------------------------------------------------------")
                print("Searching in:", current_path)

            # Lowercasing the whole text
            lowercase_text = current_page.text.lower()

            # Tokenizing text
            page_tokens = word_tokenize(lowercase_text)

            # Removing stopwords
            filtered_tokens = [token for token in page_tokens if token not in stop_words_slovene and token not in string.punctuation]

            frequency = 0
            indexes = []
            snippet = []
            snippet_count = 0

            # Search for the tokens
            for i in range(0, len(filtered_tokens)):

                if snippet_count == MAX_SNIPPET:
                    break

                if filtered_tokens[i] in arguments:
                    indexes.append(i)

                    if i - 3 <= 0:
                        snippet.extend(filtered_tokens[max(0, i-3):i])
                    else:
                        if len(snippet) == 0 or snippet[len(snippet) - 1] != "...":
                            snippet.append("...")
                        snippet.extend(filtered_tokens[i - 3: i])

                    if i + 4 >= len(filtered_tokens):
                        snippet.extend(filtered_tokens[i:min(i+4, len(filtered_tokens))])
                    else:
                        snippet.extend(filtered_tokens[i:i+4])
                        snippet.append("...")

            frequency += len(indexes)

            if frequency > 0:
                pages.append((current_path, frequency, indexes, snippet))

# Sort pages retrieved in descending order
pages.sort(key=lambda x: x[1], reverse=True)

for page in pages:
    print(f"\tHits: {page[1]}\n\t\tDoc: '{page[0]}'\n\t\tIndexes: {page[2]}\n\t\tSnippet: {' '.join(page[3])}")

print()
print("----------------------------------------------------")
print("Search time: %s seconds" % (time.time() - start_time))
print("----------------------------------------------------")