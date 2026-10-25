import os
import requests
url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?fq=obamacare&page=1&begin_date=20160101&end_date=20161231&api-key=' + os.environ.get('NYT_API_KEY', '')
response = requests.get(url)
data = response.json()
