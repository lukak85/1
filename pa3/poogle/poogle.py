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
            st = soup.text
            for argument in at:

                # Find all the occurences of the value
                lval = st.find(argument)

                # TODO - do this nicer
                # Try with capitalising the letter
                if lval < 0:
                    argument = argument.capitalize()
                    lval = st.find(argument)
                # Try with capitalising all letters
                if lval < 0:
                    argument = argument.upper()
                    lval = st.find(argument)

                if lval >= 0:
                    val = lval
                    WORD_NO = 3

                    # This is for counting how many words on each side of our word we print out
                    # (which we count using number of whitespaces), and where the said spaces appear
                    bottomInd = val - 1
                    bottomWords = 0
                    topInd = val + len(argument) + 2
                    topWords = 0
                    
                    while bottomWords < WORD_NO and bottomInd > 0:
                        bottomInd -= 1
                        if st[bottomInd] == " ":
                            bottomWords += 1

                    while topWords < WORD_NO and topInd < len(st):
                        if st[topInd] == " ":
                            topWords += 1
                        topInd += 1

                    if bottomInd == 0:
                        display_text += st[:val] + "<b>" + st[val:val + len(argument)] + "</b>" + st[val + len(argument):topInd] + "..."
                    elif topInd == len(st):
                        display_text += "..." + st[bottomInd:val] + "<b>" + st[val:val + len(argument)] + "</b>" + st[val + len(argument):]
                    else:
                        display_text = "..." + st[bottomInd:val] + "<b>" + st[val:val + len(argument)] + "</b>" + st[val + len(argument):topInd] +  "..."
            
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