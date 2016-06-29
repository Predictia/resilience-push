import base64
import requests

def getToken(domain, user, secret):
	request_token_url = domain + "oauth/token"
	payload = {'grant_type':'client_credentials','scope':'read'}
	auth_header = base64.b64encode(str(user + ':' + secret).encode())
	headers = {'Authorization': 'Basic %s' % auth_header}
	response = requests.post(request_token_url, data=payload, headers=headers, verify=True)
	if response.status_code != 200:
		print('Invalid token request')
		raise ValueError('Invalid token request')
	token_info = response.json()
	return token_info['access_token']

def getGlobalForecast(domain, token, application, forecastStartTime):
	"""Fetches the global forecast for a concrete forecastStartTime"""
	params = "application=" + application + "&product=Global Forecast&forecastStartTime=" + forecastStartTime
	request_data_url = domain + "outcomes/search/parameters?"+params
	headers = {'Authorization': 'Bearer %s' %token}
	response = requests.get(request_data_url, headers=headers, verify=True)
	if response.status_code != 200:
		print('Invalid data request')
		raise ValueError('Invalid data request')
	data = response.json()
	if '_embedded' not in data:
		print('No data found for ' + forecastStartTime)
		raise ValueError('No data found for ' + forecastStartTime)
	data = data["_embedded"]
	if 'outcomes' not in data:
		print('No data found for ' + forecastStartTime)
		raise ValueError('No data found for ' + forecastStartTime)
	return base64.b64decode(data["outcomes"][0]["results"][0])

def getPointForecast(domain, token, application, id):
	params = "application=" + application + "&product=Point Details&stationId=" + id
	request_data_url = domain + "outcomes/search/parameters?"+params
	headers = {'Authorization': 'Bearer %s' %token}
	response = requests.get(request_data_url, headers=headers, verify=True)
	if response.status_code != 200:
		print('Invalid data request')
		raise ValueError('Invalid data request')
	data = response.json()
	if '_embedded' not in data:
		print('No data found for ' + id)
		raise ValueError('No data found for ' + id)
	data = data["_embedded"]
	if 'outcomes' not in data:
		print('No data found for ' + id)
		raise ValueError('No data found for ' + id)
	return base64.b64decode(data["outcomes"][0]["results"][0])

def download_from_api(domain, user, secret, application, ftime, global_file_location, json_dir_location):
	forecastStartTime = ftime.strftime("%Y%m%d%H") + "Z" # 2015110100Z
	token = getToken(domain, user, secret)
	globalData = getGlobalForecast(domain, token, application, forecastStartTime)
	with open(global_file_location, 'w') as file_:
		file_.write(globalData)
	lines = globalData.splitlines(True)
	count = 0
	for line in lines:
		count = count+1
		if(count==1):
			continue
		stationId = line.split("\t")[0]
		localData = getPointForecast(domain, token, application, stationId)
		with open(json_dir_location + '/%s.json' %stationId, 'w') as file_:
			file_.write(localData)
		print('Downloaded station %s (%d,%d)' %(stationId,count-1,len(lines)-1))
