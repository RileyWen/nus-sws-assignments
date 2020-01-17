#!/usr/bin/python
#IBM personality insights example using Python Flask
import os
from ibm_watson import PersonalityInsightsV3
from flask import Flask, redirect, url_for, request, render_template
import json
from os.path import join, dirname
from werkzeug import secure_filename
from json2html import *

app = Flask(__name__)
#Initiating personality insights service
#You need to update iam_apikey and url according to the credentials of your personality insights service
personality_insights = PersonalityInsightsV3(
	version='2019-06-30',
	iam_apikey='SjKxYrOsxS1LCvGMtzErJnHPUXMfPWilSJ01pvfbjjAR',
    url='https://gateway-tok.watsonplatform.net/personality-insights/api'
)

#when user lands on the homepage, we redirect to the pi.html page
@app.route('/')
def home():
	return redirect(url_for('static', filename='pi.html'))

#handling the form data (upload) form pi.html
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f = request.files['file']
		f.save(secure_filename(f.filename))
		#once the file is uploaded, it is sent to the personality insights service by calling the API

	with open(join(dirname(__file__), f.filename)) as profile_f:
		profile = personality_insights.profile(
			profile_f.read(),
			'application/json',
			content_type='text/plain',
			consumption_preferences=True,
			raw_scores=True
		).get_result()
	#display the resulting json output in a structured way as a table
	return json2html.convert(json = profile)

if __name__ == '__main__':
	#server port is 8080
	port = int(os.getenv('PORT', 8080))
	app.run(host='0.0.0.0', port=port, debug=False)

