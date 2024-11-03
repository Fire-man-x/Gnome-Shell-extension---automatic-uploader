import os
import requests
from bs4 import BeautifulSoup

# credentials
username = os.getenv('GNOME_USERNAME')
password = os.getenv('GNOME_PASSWORD')

userAgent = 'GnomeShellExtensionUploader/1.0'

# URL for login
login_url = "https://extensions.gnome.org/accounts/login/"
upload_url = "https://extensions.gnome.org/upload/"

# 1. Load login page and obtain CSRF token
session = requests.Session()

# 2. Load login page
response = session.get(login_url)

# check if everything is ok
if response.status_code == 200:
	document = BeautifulSoup(response.text, 'html.parser')
	csrf_token = document.find('input', {'name': 'csrfmiddlewaretoken'})['value']

	print(document.find('h3'))

	# get CSRF token from cookies
	csrf_cookie = session.cookies.get('csrftoken')
else:
	print("Cannot load page.")
	exit()

# 3. Send login form on login page with CSRF token
login_data = {
	'username': username,
	'password': password,
	'csrfmiddlewaretoken': csrf_token
}
headers = {
	'Referer': login_url,
	'User-Agent': userAgent,
	'Cookie': f'csrftoken={csrf_cookie}',
	'Connection': 'keep-alive'
}
login_response = session.post(login_url, data=login_data, headers=headers)

if login_response.status_code == 200:
	print("Login was successed.")
else:
	print(f"Error in login: {login_response.status_code}")
	print(login_response.text)


# 4. Load upload page
print('')
response = session.get(upload_url)

# check if everything is ok
if response.status_code == 200:
	document = BeautifulSoup(response.text, 'html.parser')
	csrf_token = document.find('input', {'name': 'csrfmiddlewaretoken'})['value']

	print(document.find('h3'))
else:
	print("Cannot load upload page.")
	exit()

# 5. Send upload form on upload page with CSRF token and file
upload_form_data = {
	'shell_license_compliant': 'on',
	'tos_compliant': 'on',
	'csrfmiddlewaretoken': csrf_token
}
headers = {
	'Referer': upload_url,
	#'Host': 'extensions.gnome.org',
	#'Origin': 'https://extensions.gnome.org/upload/',
	'User-Agent': userAgent,
	'Connection': 'keep-alive',
}
files = {'source': open('gnome-shell-extension.zip', 'rb')}

# 6. Send POST request with data from form, CSRF token, headers, files, cookies
upload_response = session.post(upload_url, data=upload_form_data, headers=headers, files=files, cookies=session.cookies, allow_redirects=False)

# 7. Response
if upload_response.status_code == 200:
	print("Upload was successed.")
elif upload_response.status_code == 302:
	print('')
	print(f"Redirect detected. URL for redirect: {upload_response.status_code}")
	print(upload_response.headers['Location'])
else:
	print(f"Error in upload: {upload_response.status_code}")
	print(upload_response.text)