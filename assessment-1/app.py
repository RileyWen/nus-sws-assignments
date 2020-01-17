#!/usr/bin/python
# IBM personality insights example using Python Flask
import os
from ibm_watson import PersonalityInsightsV3
import ibm_db
from flask import Flask, redirect, url_for, request, render_template
from os.path import join, dirname
from werkzeug.utils import secure_filename
from json2html import *
import logging

app = Flask(__name__)

# Initiating personality insights service
# You need to update iam_apikey and url according to the credentials of your personality insights service
personality_insights = PersonalityInsightsV3(
    version='2019-06-30',
    iam_apikey='SjKxYrOsxS1LCvGMtzErJnHPUXMfPWilSJ01pvfbjjAR',
    url='https://gateway-tok.watsonplatform.net/personality-insights/api'
)

# TODO: establish a connection to the database

db_conn = ibm_db.connect(
    "DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-dal09-04.services.dal.bluemix.net;"
    "PORT=50000;PROTOCOL=TCPIP;UID=sjn94170;PWD=06+v12xcl75wkzt9", '', '')

# Function to Insert data to the created table
def db_insert(db_conn_, insert_query):
    try:
        statement = ibm_db.exec_immediate(db_conn_, insert_query)
        ibm_db.free_stmt(statement)

    except Exception as e:
        logging.error("The dbInsert operation error is %s" % (e))
        return False
    except:
        logging.error("The dbInsert operation error is %s" % (ibm_db.stmt_errormsg()))
        return False
    return True


# when user lands on the homepage, we redirect to the pi.html page
@app.route('/')
def home():
    return redirect(url_for('static', filename='pi.html'))


# handling the form data (upload) form pi.html
@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        person_name = f.filename.split('.')[0]
    # once the file is uploaded, it is sent to the personality insights service by calling the API
    with open(join(dirname(__file__), f.filename), encoding='utf-8') as profile_f:
        profile = personality_insights.profile(
            profile_f.read(),
            'application/json',
            content_type='text/plain',
            consumption_preferences=True,
            raw_scores=True
        ).get_result()

    print(profile)

    # TODO: Filter the information listed under "values" property in the json output. You can get this from jsondict
    #  dictionary.
    personality = profile['values']
    personality_filtered = {}
    for big5_item in personality:
        print(big5_item['name'])
        personality_filtered.update({
            big5_item['name'].split()[0].replace('-', '_').lower(): round(big5_item['raw_score'], 2)
        })
    print(personality_filtered)

    # TODO: Write an SQL query to include a new entry with the filtered scores.

    first_item = True
    insert_query_1 = "INSERT INTO SJN94170.PI_CSV(\"name\","
    insert_query_2 = " VALUES(\'" + person_name + "\',"
    for key, value in personality_filtered.items():
        if first_item:
            first_item = False
        else:
            insert_query_1 += ','
            insert_query_2 += ','

        insert_query_1 += '"' + key + '"'
        insert_query_2 += str(value)
    insert_query_1 += ')'
    insert_query_2 += ')'

    insert_query = insert_query_1 + insert_query_2
    # print(insert_query)

    result = db_insert(db_conn, insert_query)
    if result:
        print('Insert succedded!')

    # concatenating HTML code into a variable so that it could be rendered on the web browser.
    htmltext = '<h2>Personality Values</h2></br>'
    htmltext += '<table border="1"> <tr> <th> Personality Property</th> <th>Value</th></tr>'

    # TODO: Concatenate the filtered scores into HTML

    table = json2html.convert(json=personality_filtered)
    # print(table)
    htmltext += table

    htmltext += '</table>'
    return htmltext


if __name__ == '__main__':
    # server port is 8080
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
