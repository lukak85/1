import sqlite3
conn = sqlite3.connect('inverted-index.db')

import sys
import time

MAX_SNIPPET = 1
MAX_PAGES = 5
GET_SNIPPET = True



def get_snippet(j, c):
    tc = c.execute('''
            SELECT word
            FROM Posting p
            WHERE
                p.documentName = \'''' + row[0] + '''\'
            AND
            (
                (p.indexes) LIKE \'%''' + str(j) + '''%\'
            )
            LIMIT 1;
        ''')

    for r in tc:
        return r[0]
    
    return ""


arguments = "\'" + sys.argv[1] + "\'"
for arg in sys.argv[2:]:
    arguments += ", " + "\'" + arg.lower() + "\'"


start_time = time.time()

c = conn.cursor()

# Looking for the document that contain the words
cursor = c.execute('''
    SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs, word
    FROM Posting p
    WHERE
        p.word IN (''' + arguments + ''')
    GROUP BY p.documentName
    ORDER BY freq DESC;
''')

pages = []

# Save all hits in an object
for row in cursor:
    pages.append(row)

# Go trough all the hits and get their snippets
pi = 0
for row in pages:

    snippet = []
    indexes = row[2].split(",")

    if GET_SNIPPET:

        for i in range(min(len(indexes), MAX_SNIPPET)):
            ci = int(indexes[i])

            if len(snippet) == 0 or snippet[len(snippet) - 1] != "...":
                if ci - MAX_SNIPPET > 0:
                    snippet.append("...")
            
            for j in range(ci - 3, ci + 4):
                if j == ci:
                    snippet.append(row[3])
                else:
                    snippet_word = get_snippet(j, c)
                    if snippet_word != "":
                        snippet.append(snippet_word)

            snippet.append("...")

        if pi == MAX_PAGES:
            break

        pi += 1

    print(f"\tHits: {row[1]}\n\t\tDoc: '{row[0]}'\n\t\tIndexes: {row[2]}\n\t\tSnippet: '{' '.join(snippet)}'")
# You should close the connection when stopped using the database.
conn.close()

print()
print("----------------------------------------------------")
print("Search time: %s seconds" % (time.time() - start_time))
print("----------------------------------------------------")
