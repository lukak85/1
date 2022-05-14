import sqlite3
conn = sqlite3.connect('inverted-index.db')

import sys
import time



arguments = "\'" + sys.argv[1] + "\'"
for arg in sys.argv[2:]:
    arguments += ", " + "\'" + arg + "\'"


start_time = time.time()

c = conn.cursor()

# Looking for the document that contain the words
cursor = c.execute('''
    SELECT p.documentName AS docName, SUM(frequency) AS freq, GROUP_CONCAT(indexes) AS idxs
    FROM Posting p
    WHERE
        p.word IN (''' + arguments + ''')
    GROUP BY p.documentName
    ORDER BY freq DESC;
''')

# Displaying the hits
for row in cursor:
    print(f"\tHits: {row[1]}\n\t\tDoc: '{row[0]}'\n\t\tIndexes: {row[2]}")

# You should close the connection when stopped using the database.
conn.close()

end_time = time.time()
print("Search time: %s seconds ---" % (time.time() - start_time))