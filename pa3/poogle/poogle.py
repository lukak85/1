import sqlite3
from flask import Flask, render_template, send_from_directory, request
app = Flask(__name__, template_folder='static')
from bs4 import BeautifulSoup

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

            for argument in at:

                # Find all the occurences of the value
                lval = soup.text.find(argument)

                # TODO - do this nicer
                # Try with capitalising the letter
                if lval < 0:
                    argument = argument.capitalize()
                    lval = soup.text.find(argument)
                # Try with capitalising all letters
                if lval < 0:
                    argument = argument.upper()
                    lval = soup.text.find(argument)

                if lval >= 0:
                    val = lval
                    NO_T = 50

                    print(soup.text[val:val + len(argument)])

                    if val - NO_T < 0:
                        display_text += soup.text[:val] + "<b>" + soup.text[val:val + len(argument)] + "</b>" + soup.text[val + len(argument): val + NO_T] + "..."
                    elif val + NO_T > len(soup.text):
                        display_text += "..." + soup.text[val - NO_T:val] + "<b>" + soup.text[val:val + len(argument)] + "</b>" + soup.text[val + len(argument):]
                    else:
                        display_text = "..." + soup.text[val - NO_T:val] + "<b>" + soup.text[val:val + len(argument)] + "</b>" + soup.text[val + len(argument): val + NO_T] +  "..."
            
            html += """
                    <tr class='box'>
                        <td><a href='""" + page_link + """'>""" + title + """</a><i>""" + page_link + """</i> (""" + str(row[1]) + """ hits)</td>
                        <td>""" + display_text + """</td>
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