from ntpath import join
import sqlite3
from flask import Flask, render_template, send_from_directory, request
app = Flask(__name__, template_folder='static')
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

import time

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/search/style.css")
def styles():
    return send_from_directory("static", "style.css")

@app.route('/search/', methods=['GET', 'POST'])
def my_link():
    print(request.method)
    if request.method=='POST':
        arguments = request.form.get('query')
        at = arguments.split(" ")
        ata = ["\'" + token + "\'" for token in at]
        arguments = ", ".join(ata)
        print(arguments)

        conn = sqlite3.connect('../implementation-indexing/inverted-index.db')
        c = conn.cursor()

        start_time = time.time()
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
        html = """<head>
            <title>Results for \"""" + request.form.get('query') + """\"</title>
            <meta charset=utf-8>

            <link rel="stylesheet" href="style.css">
        </head>
        <body>
        <h1>Poogle</h1>
        <form action="/search/" method="post">
            <input type="text" name="query" />
            <input type="submit" value="Search" />
        </form>
        <h4>Search results gathered in """ + str(time.time() - start_time) + """ seconds</h4>"""

        html += "<table><tbody>"
        i = 0
        for row in cursor:
            page_link = "..\data" + row[0]
            f = open(page_link, 'r', encoding="utf8")
            soup = BeautifulSoup(f.read(), 'lxml')
            title = soup.find('title').string
            display_text = ""

            tokens = word_tokenize(soup.text)
            tokensl = word_tokenize(soup.text.lower())
            for argument in at:

                # Find all the occurences of the value
                try:
                    ind = tokensl.index(argument)
                except:
                    continue

                snippet = []
                if ind - 3 <= 0:
                    snippet.extend(tokens[max(0, ind - 3):ind])
                else:
                    if len(snippet) == 0 or snippet[len(snippet) - 1] != "...":
                        snippet.append("...")
                    snippet.extend(tokens[ind - 3: ind])

                snippet.append("<b>" + tokens[ind] + "</b>")

                if ind + 4 >= len(tokens):
                    snippet.extend(tokens[ind:min(ind + 4, len(tokens))])
                else:
                    snippet.extend(tokens[ind + 1:ind + 4])
                    snippet.append("...")
            
            html += """
                    <tr class='box'>
                        <td><a href='""" + page_link + """'>""" + title + """</a><i>""" + page_link + """</i> (""" + str(row[1]) + """ hits)</td>
                        <td>""" + ' '.join(snippet) + """</td>
                    </tr>
                    """

            if i > 20:
                break
            i += 1

        html += "</tbody></table></body>"

        # You should close the connection when stopped using the database.
        conn.close()

    return html

if __name__ == '__main__':
    app.run(debug=True)