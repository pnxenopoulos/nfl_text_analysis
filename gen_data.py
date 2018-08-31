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
		print("Grabbed {0} data...".format(y))
	return script_text

def write_player_df(script_text):
	''' Function to write a data frame containing player information
	@param List script_text: A list containing the pertinent javascript
	'''
	print("Writing player information data frame...")
	player_data_frames = []
	for s in script_text:
		player_text = re.findall(r'{"personId"(.*?)}', s)
		year, playerId, firstName, lastName, hasAnalysis, pos, expertGrade, pick = [], [], [], [], [], [], [], []
		for p in player_text:
			year_pre = re.findall(r'nfl.global.dt.year(.*)', s)[0]
			year.append(int(re.findall(r'\'(.*)\'', year_pre)[0]))
			playerId.append(re.findall(r':(.*?),' ,p)[0])
			firstName.append(re.findall(r'"firstName":"(.*?)",' ,p)[0])
			lastName.append(re.findall(r'"lastName":"(.*?)",' ,p)[0])
			hasAnalysis.append(re.findall(r'"hasAnalysis":(.*?),' ,p)[0])
			pos.append(re.findall(r'"pos":"(.*?)",' ,p)[0])
			expertGrade.append(re.findall(r'"expertGrade":(.*?),' ,p)[0])
			pick.append(re.findall(r'"pick":(.*?),' ,p)[0])
		player_dict = {"year": year, "player_id": playerId, "first_name": firstName, "last_name": lastName, "hasAnalysis": hasAnalysis, "position": pos ,"grade": expertGrade, "pick": pick}
		player_data_frames.append(pd.DataFrame.from_dict(player_dict))
		player_data_concat = pd.concat(player_data_frames)
		player_data_concat = player_data_concat[player_data_concat['hasAnalysis'] == 'true']
		player_data_concat = player_data_concat[player_data_concat['grade'] != 'null']
		player_data_concat['grade'] = pd.to_numeric(player_data_concat['grade'])
		#player_data_concat.loc(player_data_concat['year'] < 2014, ["grade"]) = player_data_concat.loc[x['year'] < 2014, ["grade"]]/10
	
	return player_data_concat

def get_player_text(player_data):
	''' Function to get the player textual data
	@param DataFrame player_data: A data frame containing basic player info like ids and year
	'''
	for index, row in player_data.iterrows():
		print("Retrieving data for {0} {1} in {3}...".format(player_fn, player_ln, player_year))
		player_year = row['year']
		player_fn = row['first_name']
		player_ln = row['last_name']
		player_id = row['player_id']
		url = "http://www.nfl.com/draft/{0}/profiles/{1}-{2}?id={3}".format(player_year, player_fn, player_ln, player_id)
		raw_html = get_page(url)
		html = BeautifulSoup(raw_html, 'html.parser')
		article_nodes = html.select('article')	
	return article_nodes

script_nodes = get_script_nodes()
player_data = write_player_df(script_nodes)
test = get_player_text(player_data)