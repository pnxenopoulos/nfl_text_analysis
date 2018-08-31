''' Script to generate clean NFL textual data on the draft
@author: Peter Xenopoulos
@website: www.peterxeno.com
'''

import numpy as np
import pandas as pd
import re

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def get_page(url):
	''' Function to grab the html of a page
	@param String url: The string of the URL
	'''
	try:
		with closing(get(url, stream=True)) as resp:
			if good_response(resp):
				return resp.content
			else:
				return None
	except RequestException as e:
		log_error('Error during request for {0} : {1}'.format(url, str(e)))
		return None

def good_response(resp):
	''' Function to return true if the response is HTML
	@param String resp: Text that we to check if HTML
	'''
	content_type = resp.headers['Content-Type'].lower()
	return (resp.status_code == 200
		and content_type is not None
		and content_type.find('html') > -1)

def log_error(e):
	''' Function to simply print the error
	@param String e: Error string
	'''
	print(e)

def get_script_nodes():
	''' Function to return the text of the script for each year's page
	Keep years and script_position constant -- these are hardcoded by necessity
	'''
	years = [2012, 2013, 2014, 2015, 2016, 2017]
	script_position = [16, 14, 14, 14, 14, 14]
	script_text = []
	for i in range(6):
		y = years[i]
		pos = script_position[i]
		url = "http://www.nfl.com/draft/{0}/tracker#dt-tabs:dt-by-round/dt-by-grade-input:14/dt-by-round-input:1".format(y)
		raw_html = get_page(url)
		html = BeautifulSoup(raw_html, 'html.parser')
		script_nodes = html.select('script')
		script_text.append(str(script_nodes[pos]))
	return script_text

def write_player_df(script_text):
	''' Function to write a data frame containing player information
	@param List script_text: A list containing the pertinent javascript
	'''
	player_data_frames = []
	for s in script_text:
		player_text = re.findall(r'{"personId"(.*?)}', s)
		playerId, firstName, lastName, hasAnalysis, pos, expertGrade, pick = [], [], [], [], [], [], []
		for p in player_text:
			playerId.append(re.findall(r':(.*?),' ,p)[0])
			firstName.append(re.findall(r'"firstName":"(.*?)",' ,p)[0])
			lastName.append(re.findall(r'"lastName":"(.*?)",' ,p)[0])
			hasAnalysis.append(re.findall(r'"hasAnalysis":(.*?),' ,p)[0])
			pos.append(re.findall(r'"pos":"(.*?)",' ,p)[0])
			expertGrade.append(re.findall(r'"expertGrade":(.*?),' ,p)[0])
			pick.append(re.findall(r'"pick":(.*?),' ,p)[0])
		player_dict = {"player_id": playerId, "first_name": firstName, "last_name": lastName, "hasAnalysis": hasAnalysis, "position": pos ,"grade": expertGrade, "pick": pick}
		player_data_frames.append(pd.DataFrame.from_dict(player_dict))
	return player_data_frames

