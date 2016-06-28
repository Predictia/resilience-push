import base64
import requests

domain = "http://178.62.156.204/"
application = "6"
forecastStartTime = "2015110100Z"
user = "RESILIENCE.ro"
secret = "4e975e24-2124-4572-8b74-f6264907093e"

def getToken():
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

def getGlobalForecast(startTime):
	params = "application=" + application + "&product=Global Forecast&forecastStartTime=" + startTime
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
	return base64.b64decode(str(data["outcomes"][0]))

def getPointForecast(id):
	params = "application=" + application + "&product=Point Details&stationId=" + id
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

# gets the token
token = getToken()

# gets the global forecast for a concrete forecastStartTime
globalData = getGlobalForecast(forecastStartTime)

lines = globalData.splitlines(True)
count = 0
for line in lines:
	count = count+1
	if(count==1):
		continue
	stationId = line.split("\t")[0]
	localData = getPointForecast(stationId)
	with open('/tmp/json/%s.json' %stationId, 'w') as file_:
		file_.write(localData)
	print('Downloaded station %s (%d,%d)' %(stationId,count-1,len(lines)-1))
