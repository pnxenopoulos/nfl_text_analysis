''' Script to generate clean NFL textual data on the draft
@author: Peter Xenopoulos
@website: www.peterxeno.com
'''

import numpy as np
import pandas as pd

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
			if is_good_response(resp):
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
	'''
	Function to simply print the error
	@param String e: Error string
	'''
	print(e)

