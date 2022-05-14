import sqlite3

from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup

import os
import string
from stopwords import stop_words_slovene

DEBUG_MODE = False



# Check if there's database present, if not, create it
if os.path.isfile('./inverted-index.db'):
    print("Database already exists!")
    conn = sqlite3.connect('inverted-index.db')
else:
    conn = sqlite3.connect('inverted-index.db')

    # Create table
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IndexWord (
            word TEXT PRIMARY KEY
        );
    ''')

    c.execute('''
        CREATE TABLE Posting (
            word TEXT NOT NULL,
            documentName TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            indexes TEXT NOT NULL,
            PRIMARY KEY(word, documentName),
            FOREIGN KEY (word) REFERENCES IndexWord(word)
        );
    ''')

    # Save (commit) the changes
    conn.commit()


for root, _, files in os.walk("../data"):

    for file in files:

        if file.endswith(".html"):
            f = open(os.path.join(root, file), 'r', encoding="utf8")
            
            current_path = os.path.join(root, file).replace("../data", "")

            current_page = BeautifulSoup(f.read(), 'lxml')

            print("----------------------------------------------------------------------------------")
            print("Currently indexing:", current_path)

            # Lowercasing the whole text
            lowercase_text = current_page.text.lower()

            # Tokenizing text
            page_tokens = word_tokenize(lowercase_text)

            # Removing stopwords
            filtered_tokens = [token for token in page_tokens if token not in stop_words_slovene and token not in string.punctuation]

            checked_tokens = []

            # Inserting the words into the database
            for token in filtered_tokens:

                if token in checked_tokens:
                    continue

                # Array which stores indexes at which token appears
                indexes = []
                for i in range(0, len(filtered_tokens)):
                    if token == filtered_tokens[i]:
                        indexes.append(i)

                # Try adding the word; it may already have been added though
                try:
                    c = conn.cursor()

                    c.execute('''
                        INSERT INTO IndexWord VALUES
                            (''' + '\'' + token + '\'' + ''');
                    ''')
                except:
                    if DEBUG_MODE:
                        print("Word \'" + token + "\' already exists in the database")

                try:
                    c.execute('''
                        INSERT INTO Posting VALUES 
                            (''' + '\'' + token + '\'' + ''', ''' + '\'' + current_path + '\'' + ''', ''' + str(len(indexes)) + ''', ''' + '\'' + str(indexes) + '\'' + ''');
                    ''')
                except:
                    if DEBUG_MODE:
                        print("Idk what could have gone wrong yet")

                # Save (commit) the changes
                conn.commit()
                
                # Mark the token as checked
                checked_tokens.append(token)
                

# You should close the connection when stopped using the database.
conn.close()